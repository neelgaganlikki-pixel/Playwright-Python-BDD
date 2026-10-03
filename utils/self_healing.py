import json
import os
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from playwright.sync_api import Locator, Page

from utils.logger import get_logger

logger = get_logger("SelfHealing")


# =============================================================================
# Custom Exception
# =============================================================================

class SelfHealingError(Exception):
    """
    Raised when an element interaction fails after all primary and fallback
    locators have been exhausted.
    """

    def __init__(
        self,
        element_name: str,
        page_name: str,
        action: str,
        primary_locator: str,
        fallbacks_tried: List[str],
        reason: str,
        original_exception: Optional[Exception] = None,
    ):
        self.element_name = element_name
        self.page_name = page_name
        self.action = action
        self.primary_locator = primary_locator
        self.fallbacks_tried = fallbacks_tried
        self.reason = reason
        self.original_exception = original_exception

        message = (
            f"\n[SELF-HEALING ERROR]\n"
            f"Element: {element_name}\n"
            f"Page: {page_name}\n"
            f"Action: {action}\n"
            f"Primary Locator: {primary_locator}\n"
            f"Fallbacks Tried ({len(fallbacks_tried)}): {', '.join(fallbacks_tried) if fallbacks_tried else 'None'}\n"
            f"Reason: {reason}\n"
            f"Original Exception: {original_exception}"
        )
        super().__init__(message)


# =============================================================================
# Data Models for Tracking & Reporting
# =============================================================================

@dataclass
class HealingRecord:
    timestamp: str
    element_name: str
    page_name: str
    action: str
    primary_locator: str
    successful_locator: str
    attempt_number: int
    fallbacks_attempted: List[str]
    success: bool
    details: str = ""


# =============================================================================
# Central Self-Healing Engine
# =============================================================================

class SelfHealingEngine:
    """
    Central, thread-safe Self-Healing Engine for Playwright automation.
    Recovers from locator breakages by evaluating fallback candidates in priority order,
    caches successful healed selectors, and produces execution summaries.
    """

    _instance: Optional["SelfHealingEngine"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "SelfHealingEngine":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        self._records: List[HealingRecord] = []
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._stats_lock = threading.RLock()

        # Configuration
        self.enabled = os.getenv("SELF_HEALING_ENABLED", "true").strip().lower() in ("true", "1", "yes")
        self.max_attempts = int(os.getenv("SELF_HEALING_MAX_ATTEMPTS", "3"))
        self.save_locators = os.getenv("SELF_HEALING_SAVE_LOCATORS", "true").strip().lower() in ("true", "1", "yes")
        self.primary_timeout_ms = int(os.getenv("SELF_HEALING_PRIMARY_TIMEOUT", "5000"))
        self.fallback_timeout_ms = int(os.getenv("SELF_HEALING_FALLBACK_TIMEOUT", "3000"))

        # Storage directory and file
        self.storage_path = Path("reports") / "healed_locators.json"
        self._load_cache()
        self._initialized = True

    # -------------------------------------------------------------------------
    # Cache Persistence (reports/healed_locators.json)
    # -------------------------------------------------------------------------

    def _load_cache(self) -> None:
        """Load previously healed locators from disk if present."""
        if not self.storage_path.exists():
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                self._cache = json.load(f)
            logger.info("[SELF-HEALING] Loaded %d cached healed locators from %s", len(self._cache), self.storage_path)
        except Exception as e:
            logger.warning("[SELF-HEALING] Could not load healed locator cache: %s", e)
            self._cache = {}

    def _save_cache(self) -> None:
        """Atomically persist healed locators to disk."""
        if not self.save_locators:
            return
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path = self.storage_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=4)
            temp_path.replace(self.storage_path)
        except Exception as e:
            logger.warning("[SELF-HEALING] Failed to save healed locators cache: %s", e)

    def _cache_key(self, page_name: str, element_name: str) -> str:
        return f"{page_name}.{element_name}"

    def record_healed_locator(
        self,
        page_name: str,
        element_name: str,
        original_locator: str,
        healed_locator: str,
    ) -> None:
        """Store a successful healed locator into persistent storage."""
        with self._stats_lock:
            key = self._cache_key(page_name, element_name)
            current_entry = self._cache.get(key, {})
            success_count = current_entry.get("success_count", 0) + 1

            self._cache[key] = {
                "original": original_locator,
                "healed": healed_locator,
                "timestamp": datetime.now().isoformat(),
                "success_count": success_count,
            }
            self._save_cache()

    # -------------------------------------------------------------------------
    # Core Interaction & Healing Dispatcher
    # -------------------------------------------------------------------------

    def execute_with_healing(
        self,
        page: Page,
        page_name: str,
        element_name: str,
        primary_locator: str,
        action_name: str,
        action_fn: Callable[[Locator], Any],
        fallbacks: Optional[List[str]] = None,
        timeout_ms: Optional[int] = None,
        is_query: bool = False,
    ) -> Any:
        """
        Executes an action against an element. If the primary locator fails:
        1. Checks persistent cache for a previously verified healed locator.
        2. Tries user-provided and priority fallback locators sequentially.
        3. Validates visibility / enabled state before executing.
        4. Logs the healing event and saves healed selector if successful.
        5. Raises SelfHealingError if all candidates fail.
        """
        if fallbacks is None:
            fallbacks = []

        cache_key = self._cache_key(page_name, element_name)
        cached_healed = self._cache.get(cache_key, {}).get("healed")

        # Compile candidates in priority order:
        # 1. Previously cached healed locator (if exists and distinct from primary)
        # 2. Primary locator
        # 3. Explicit fallbacks provided by caller
        candidates: List[str] = []
        if cached_healed and cached_healed != primary_locator:
            candidates.append(cached_healed)
        if primary_locator not in candidates:
            candidates.append(primary_locator)
        for fb in fallbacks:
            if fb and fb not in candidates:
                candidates.append(fb)

        # If self-healing is disabled, only execute with primary locator
        if not self.enabled:
            loc = page.locator(primary_locator)
            return action_fn(loc)

        logger.info("[SELF-HEALING] Searching for element: '%s' on %s (Action: %s)", element_name, page_name, action_name)
        logger.debug("[SELF-HEALING] Primary locator: %s | Candidates: %s", primary_locator, candidates)

        last_exception: Optional[Exception] = None
        attempt_number = 0
        attempted_fallbacks: List[str] = []

        # Determine individual candidate timeout
        primary_timeout = timeout_ms or self.primary_timeout_ms
        fallback_timeout = timeout_ms or self.fallback_timeout_ms

        for candidate in candidates:
            attempt_number += 1
            is_primary = (candidate == primary_locator)

            if not is_primary:
                attempted_fallbacks.append(candidate)
                logger.info("[SELF-HEALING] Attempt %d: Trying candidate: %s", attempt_number, candidate)

            current_timeout = primary_timeout if is_primary else fallback_timeout

            try:
                locator = page.locator(candidate)

                # Query actions (like is_visible) handle their own validation
                if is_query:
                    result = action_fn(locator)
                    if result:
                        if not is_primary:
                            logger.info("[SELF-HEALING] SUCCESS (Query): '%s' verified using %s", element_name, candidate)
                            self._record_success(
                                element_name, page_name, action_name, primary_locator, candidate,
                                attempt_number, attempted_fallbacks
                            )
                        return result
                    else:
                        continue

                # For interaction actions (click, fill, etc.), wait for actionable state
                locator.first.wait_for(state="visible", timeout=current_timeout)

                # Execute action
                result = action_fn(locator.first)

                # If healed via fallback:
                if not is_primary:
                    logger.info("=" * 60)
                    logger.info("[SELF-HEALING] SUCCESS: '%s' healed using fallback: %s", element_name, candidate)
                    logger.info("=" * 60)
                    self._record_success(
                        element_name, page_name, action_name, primary_locator, candidate,
                        attempt_number, attempted_fallbacks
                    )
                return result

            except Exception as ex:
                last_exception = ex
                if is_primary:
                    logger.warning(
                        "[SELF-HEALING] Primary locator failed for '%s':\n%s\nReason: %s",
                        element_name, primary_locator, ex
                    )
                else:
                    logger.debug("[SELF-HEALING] Candidate '%s' failed: %s", candidate, ex)

        # All candidates exhausted
        if not is_query:
            self._record_failure(
                element_name, page_name, action_name, primary_locator, attempted_fallbacks, str(last_exception)
            )
            raise SelfHealingError(
                element_name=element_name,
                page_name=page_name,
                action=action_name,
                primary_locator=primary_locator,
                fallbacks_tried=attempted_fallbacks,
                reason=f"All {len(candidates)} locator candidate(s) failed.",
                original_exception=last_exception,
            )

        return False


    # -------------------------------------------------------------------------
    # Record Keeping
    # -------------------------------------------------------------------------

    def _record_success(
        self,
        element_name: str,
        page_name: str,
        action: str,
        primary_locator: str,
        successful_locator: str,
        attempt_number: int,
        fallbacks_attempted: List[str],
    ) -> None:
        with self._stats_lock:
            record = HealingRecord(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                element_name=element_name,
                page_name=page_name,
                action=action,
                primary_locator=primary_locator,
                successful_locator=successful_locator,
                attempt_number=attempt_number,
                fallbacks_attempted=fallbacks_attempted,
                success=True,
                details=f"Recovered on attempt {attempt_number}",
            )
            self._records.append(record)
            self.record_healed_locator(page_name, element_name, primary_locator, successful_locator)

    def _record_failure(
        self,
        element_name: str,
        page_name: str,
        action: str,
        primary_locator: str,
        fallbacks_attempted: List[str],
        details: str,
    ) -> None:
        with self._stats_lock:
            record = HealingRecord(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                element_name=element_name,
                page_name=page_name,
                action=action,
                primary_locator=primary_locator,
                successful_locator="",
                attempt_number=len(fallbacks_attempted) + 1,
                fallbacks_attempted=fallbacks_attempted,
                success=False,
                details=details,
            )
            self._records.append(record)

    # -------------------------------------------------------------------------
    # Reporting
    # -------------------------------------------------------------------------

    def get_summary(self) -> Dict[str, Any]:
        """Returns statistical summary of self-healing operations."""
        with self._stats_lock:
            total_attempts = len(self._records)
            successful = sum(1 for r in self._records if r.success)
            failed = sum(1 for r in self._records if not r.success)
            healed_elements = [
                {
                    "element": r.element_name,
                    "page": r.page_name,
                    "action": r.action,
                    "original": r.primary_locator,
                    "healed": r.successful_locator,
                    "attempt": r.attempt_number,
                }
                for r in self._records
                if r.success
            ]
            return {
                "total_attempts": total_attempts,
                "successful": successful,
                "failed": failed,
                "healed_elements": healed_elements,
            }

    def print_summary(self) -> None:
        """Formats and outputs the self-healing summary report to console and log."""
        summary = self.get_summary()

        report_lines = [
            "\n" + "=" * 60,
            "SELF-HEALING AUTOMATION SUMMARY",
            "=" * 60,
            f"Total Healing Events: {summary['total_attempts']}",
            f"Successful Recoveries: {summary['successful']}",
            f"Failed Recoveries:     {summary['failed']}",
            "-" * 60,
        ]

        if summary["healed_elements"]:
            report_lines.append("Healed Elements Detail:")
            for item in summary["healed_elements"]:
                report_lines.append(f"  • [{item['page']}] {item['element']} (Action: {item['action']})")
                report_lines.append(f"      Original: {item['original']}")
                report_lines.append(f"      Healed:   {item['healed']}")
        else:
            report_lines.append("No elements required healing (all primary locators passed or healing disabled).")

        report_lines.append("=" * 60 + "\n")
        report_text = "\n".join(report_lines)

        print(report_text)
        logger.info(report_text)

        try:
            summary_path = Path("reports") / "self_healing_summary.json"
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=4)
        except Exception as e:
            logger.warning("[SELF-HEALING] Could not write summary JSON: %s", e)

    def reset(self) -> None:
        """Reset in-memory records (useful between test runs)."""
        with self._stats_lock:
            self._records.clear()


# Global Singleton accessor
self_healing_engine = SelfHealingEngine()
