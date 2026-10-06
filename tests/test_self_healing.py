import json
import time
from pathlib import Path
import pytest
from playwright.sync_api import Page

from utils.self_healing import SelfHealingEngine, SelfHealingError


@pytest.fixture
def clean_engine():
    """Provides a reset self-healing engine for isolated unit testing."""
    engine = SelfHealingEngine()
    engine.enabled = True
    engine.save_locators = True
    engine.primary_timeout_ms = 800
    engine.fallback_timeout_ms = 800
    engine.storage_path = Path("reports") / "test_healed_locators.json"
    if engine.storage_path.exists():
        engine.storage_path.unlink()
    engine._cache = {}
    engine.reset()
    yield engine
    if engine.storage_path.exists():
        engine.storage_path.unlink()


def test_self_healing_engine_comprehensive_suite(page: Page, clean_engine: SelfHealingEngine):
    """
    Unified comprehensive verification of the Self-Healing Locator Engine covering
    all 14 core engine capabilities in a single consolidated test:
      1. Primary Locator Succeeds Directly
      2. Primary Fails, Fallback Succeeds
      3. Multiple Fallbacks Tested in Sequence
      4. All Fallbacks Fail -> Raises SelfHealingError
      5. Click Action Healing
      6. Fill Action Healing
      7. Visibility Query Healing
      8. Disabled Element Does Not Hide Failure
      9. Hidden Element Fails Actionable Wait
      10. Timeout Behavior (Controlled and Bounded)
      11. Self-Healing Disabled Mode
      12. Healed Locator Persistence & Cache Reuse
      13. Invalid / Malformed Locator Syntax Handled Gracefully
      14. Headless Execution & Final Metrics Verification
    """
    # -------------------------------------------------------------------------
    # 1. Primary Locator Succeeds Directly
    # -------------------------------------------------------------------------
    page.set_content("<button id='submit-btn'>Submit</button>")
    clicked = []
    clean_engine.execute_with_healing(
        page=page,
        page_name="TestPage",
        element_name="SubmitButton",
        primary_locator="#submit-btn",
        action_name="click",
        action_fn=lambda loc: (loc.click(), clicked.append(True)),
        fallbacks=["button.btn-fallback", "[data-testid='submit']"],
    )
    assert len(clicked) == 1
    assert clean_engine.get_summary()["successful"] == 0

    # -------------------------------------------------------------------------
    # 2. Primary Locator Fails, Fallback Succeeds
    # -------------------------------------------------------------------------
    page.set_content("<input name='username' type='text' />")
    result = clean_engine.execute_with_healing(
        page=page,
        page_name="LoginPage",
        element_name="UsernameInput",
        primary_locator="#legacy-username-id",  # intentionally broken
        action_name="fill",
        action_fn=lambda loc: (loc.fill("admin_test"), "filled")[-1],
        fallbacks=["input[name='username']", "input[type='text']"],
    )
    assert result == "filled"
    assert page.locator("input[name='username']").input_value() == "admin_test"
    summary = clean_engine.get_summary()
    assert summary["successful"] == 1
    assert summary["healed_elements"][0]["healed"] == "input[name='username']"

    # -------------------------------------------------------------------------
    # 3. Multiple Fallbacks Tested in Sequence
    # -------------------------------------------------------------------------
    page.set_content("<button class='final-btn'>Save Changes</button>")
    clean_engine.execute_with_healing(
        page=page,
        page_name="SettingsPage",
        element_name="SaveButton",
        primary_locator="#broken-primary",
        action_name="click",
        action_fn=lambda loc: loc.click(),
        fallbacks=[
            "#broken-fallback-1",
            ".broken-fallback-2",
            "button.final-btn",  # 3rd candidate succeeds
        ],
    )
    summary = clean_engine.get_summary()
    assert summary["successful"] == 2
    assert summary["healed_elements"][1]["attempt"] == 4

    # -------------------------------------------------------------------------
    # 4. All Fallbacks Fail -> Raises SelfHealingError
    # -------------------------------------------------------------------------
    page.set_content("<div>Empty Container</div>")
    with pytest.raises(SelfHealingError) as exc_info:
        clean_engine.execute_with_healing(
            page=page,
            page_name="ProfilePage",
            element_name="MissingButton",
            primary_locator="#missing-1",
            action_name="click",
            action_fn=lambda loc: loc.click(),
            fallbacks=["#missing-2", "#missing-3"],
        )
    err = exc_info.value
    assert err.element_name == "MissingButton"
    assert err.page_name == "ProfilePage"
    assert len(err.fallbacks_tried) == 2
    assert clean_engine.get_summary()["failed"] == 1

    # -------------------------------------------------------------------------
    # 5. Click Action Healing
    # -------------------------------------------------------------------------
    page.set_content(
        "<button id='real-btn' onclick=\"document.body.innerHTML='<h1>Clicked!</h1>'\">Click Me</button>"
    )
    clean_engine.execute_with_healing(
        page=page,
        page_name="ClickPage",
        element_name="RealButton",
        primary_locator="#obsolete-btn",
        action_name="click",
        action_fn=lambda loc: loc.click(),
        fallbacks=["button#real-btn"],
    )
    assert "Clicked!" in page.content()

    # -------------------------------------------------------------------------
    # 6. Fill Action Healing
    # -------------------------------------------------------------------------
    page.set_content("<input id='password-field' type='password' />")
    clean_engine.execute_with_healing(
        page=page,
        page_name="LoginPage",
        element_name="PasswordField",
        primary_locator="#old-pwd",
        action_name="fill",
        action_fn=lambda loc: loc.fill("Secret123"),
        fallbacks=["input#password-field"],
    )
    assert page.locator("#password-field").input_value() == "Secret123"

    # -------------------------------------------------------------------------
    # 7. Visibility Query Healing
    # -------------------------------------------------------------------------
    page.set_content("<span class='success-banner'>Operation Complete</span>")
    visible = clean_engine.execute_with_healing(
        page=page,
        page_name="AlertPage",
        element_name="SuccessBanner",
        primary_locator=".missing-banner",
        action_name="is_visible",
        action_fn=lambda loc: loc.is_visible(),
        fallbacks=[".success-banner"],
        is_query=True,
    )
    assert visible is True

    # -------------------------------------------------------------------------
    # 8. Genuinely Missing / Disabled Element Does Not Hide Failure
    # -------------------------------------------------------------------------
    page.set_content("<button id='disabled-btn' disabled>Cannot Click</button>")
    with pytest.raises(SelfHealingError):
        clean_engine.execute_with_healing(
            page=page,
            page_name="FormPage",
            element_name="DisabledButton",
            primary_locator="#missing-primary",
            action_name="click",
            action_fn=lambda loc: loc.click(timeout=1000),
            fallbacks=["button#disabled-btn"],
            timeout_ms=1000,
        )

    # -------------------------------------------------------------------------
    # 9. Hidden Element Fails Actionable Wait
    # -------------------------------------------------------------------------
    page.set_content("<div id='hidden-div' style='display: none;'>Hidden</div>")
    with pytest.raises(SelfHealingError):
        clean_engine.execute_with_healing(
            page=page,
            page_name="ViewPage",
            element_name="HiddenElement",
            primary_locator="#missing",
            action_name="click",
            action_fn=lambda loc: loc.click(timeout=1000),
            fallbacks=["#hidden-div"],
            timeout_ms=1000,
        )

    # -------------------------------------------------------------------------
    # 10. Timeout Behavior (Controlled and Bounded)
    # -------------------------------------------------------------------------
    page.set_content("<div>No buttons here</div>")
    clean_engine.fallback_timeout_ms = 500
    start = time.time()
    with pytest.raises(SelfHealingError):
        clean_engine.execute_with_healing(
            page=page,
            page_name="TimePage",
            element_name="SlowElement",
            primary_locator="#missing-1",
            action_name="click",
            action_fn=lambda loc: loc.click(timeout=500),
            fallbacks=["#missing-2"],
            timeout_ms=500,
        )
    assert (time.time() - start) < 5.0

    # -------------------------------------------------------------------------
    # 11. Self-Healing Disabled
    # -------------------------------------------------------------------------
    page.set_content("<button id='valid-btn'>Valid</button>")
    clean_engine.enabled = False
    with pytest.raises(Exception):
        clean_engine.execute_with_healing(
            page=page,
            page_name="DisabledPage",
            element_name="TestElement",
            primary_locator="#broken-selector",
            action_name="click",
            action_fn=lambda loc: loc.click(timeout=1000),
            fallbacks=["#valid-btn"],
            timeout_ms=1000,
        )
    clean_engine.enabled = True

    # -------------------------------------------------------------------------
    # 12. Healed Locator Persistence and Reuse
    # -------------------------------------------------------------------------
    page.set_content("<input id='reused-input' value='Initial' />")
    clean_engine.execute_with_healing(
        page=page,
        page_name="FormPage",
        element_name="PersistedField",
        primary_locator="#old-field-id",
        action_name="fill",
        action_fn=lambda loc: loc.fill("UpdatedValue"),
        fallbacks=["#another-broken", "#reused-input"],
    )
    assert clean_engine.storage_path.exists()
    with open(clean_engine.storage_path, "r", encoding="utf-8") as f:
        stored = json.load(f)
    assert "FormPage.PersistedField" in stored
    assert stored["FormPage.PersistedField"]["healed"] == "#reused-input"

    # Second execution: engine should immediately check cached healed selector
    clean_engine.execute_with_healing(
        page=page,
        page_name="FormPage",
        element_name="PersistedField",
        primary_locator="#old-field-id",
        action_name="fill",
        action_fn=lambda loc: loc.fill("SecondUpdate"),
        fallbacks=["#another-broken", "#reused-input"],
    )
    assert page.locator("#reused-input").input_value() == "SecondUpdate"

    # -------------------------------------------------------------------------
    # 13. Invalid Locator Syntax Handled Gracefully
    # -------------------------------------------------------------------------
    page.set_content("<p id='valid-target'>Hello World</p>")
    text = clean_engine.execute_with_healing(
        page=page,
        page_name="SyntaxPage",
        element_name="TargetParagraph",
        primary_locator="///invalid[[[selector",  # Malformed selector
        action_name="inner_text",
        action_fn=lambda loc: loc.inner_text(),
        fallbacks=["#valid-target"],
    )
    assert text == "Hello World"

    # -------------------------------------------------------------------------
    # 14. Jenkins / Headless Execution & Metrics Verification
    # -------------------------------------------------------------------------
    page.set_content("<button class='ci-button'>CI Ready</button>")
    clean_engine.execute_with_healing(
        page=page,
        page_name="CIPage",
        element_name="CIButton",
        primary_locator="#missing-ci-btn",
        action_name="click",
        action_fn=lambda loc: loc.click(),
        fallbacks=[".ci-button"],
    )
    final_summary = clean_engine.get_summary()
    assert final_summary["successful"] >= 1
