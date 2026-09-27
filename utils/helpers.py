from pathlib import Path
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from utils.logger import get_logger

logger = get_logger("Helpers")


class PlaywrightHelper:
    """
    Playwright utility helpers providing resilient, non-blocking interaction methods
    adhering to best practices (zero time.sleep()).
    """

    @staticmethod
    def wait_for_network_idle(page: Page, timeout: int = 15000) -> None:
        """
        Wait for network activity to settle.
        """
        try:
            page.wait_for_load_state("networkidle", timeout=timeout)
        except PlaywrightTimeoutError:
            logger.warning("Network idle state timed out, proceeding with execution.")

    @staticmethod
    def safe_click(locator: Locator, timeout: int = 10000) -> None:
        """
        Wait for an element to be visible and enabled before clicking.
        """
        locator.wait_for(state="visible", timeout=timeout)
        locator.scroll_into_view_if_needed()
        locator.click()

    @staticmethod
    def safe_fill(locator: Locator, text: str, timeout: int = 10000) -> None:
        """
        Wait for an input element to be visible, clear its content, and fill with text.
        """
        locator.wait_for(state="visible", timeout=timeout)
        locator.fill("")
        locator.fill(text)

    @staticmethod
    def get_element_text(locator: Locator, timeout: int = 10000) -> str:
        """
        Safely fetch inner text from a locator.
        """
        locator.wait_for(state="visible", timeout=timeout)
        return locator.inner_text().strip()

    @staticmethod
    def take_screenshot(page: Page, name: str) -> Path:
        """
        Capture and store a timestamped screenshot in the screenshots directory.
        """
        screenshots_dir = Path(__file__).resolve().parent.parent / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        file_path = screenshots_dir / f"{name}.png"
        page.screenshot(path=str(file_path), full_page=True)
        logger.info(f"Screenshot saved to: {file_path}")
        return file_path
