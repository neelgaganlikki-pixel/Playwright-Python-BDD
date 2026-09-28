import base64
from datetime import datetime
from pathlib import Path
from typing import Any, Generator

import pytest
import pytest_html
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)

from config.config_reader import ConfigReader
from utils.logger import get_logger


# ============================================================
# Pytest-BDD Step Definition Plugins
# ============================================================

pytest_plugins = [
    "step_definitions.login_steps",
    "step_definitions.employee_steps",
    "step_definitions.leave_steps",
    "step_definitions.recruitment_steps",
    "step_definitions.buzz_steps",
]


# ============================================================
# Logger
# ============================================================

logger = get_logger(__name__)


# ============================================================
# Constants
# ============================================================

DEFAULT_TIMEOUT = 30000


# ============================================================
# Configuration Fixture
# ============================================================

@pytest.fixture(scope="session")
def config() -> ConfigReader:
    """
    Provides the project configuration for the test session.
    """
    return ConfigReader()


# ============================================================
# Test Context Fixture
# ============================================================

@pytest.fixture
def test_context() -> dict[str, Any]:
    """
    Stores test-specific data that may be shared between
    BDD steps during a test.
    """
    return {}


# ============================================================
# Scenario Lifecycle Logger Fixture
# ============================================================

@pytest.fixture(autouse=True)
def log_scenario_lifecycle(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    """
    Logs the start, completion, and duration of every test scenario.
    """
    scenario_name = request.node.name
    logger.info("=" * 80)
    logger.info(">>> TEST SCENARIO STARTED: %s", scenario_name)
    logger.info("=" * 80)
    start_time = datetime.now()

    yield

    duration = (datetime.now() - start_time).total_seconds()
    logger.info("-" * 80)
    logger.info(
        ">>> TEST SCENARIO FINISHED: %s | Duration: %.2fs",
        scenario_name,
        duration,
    )
    logger.info("=" * 80)



# ============================================================
# Playwright Engine Fixture
# ============================================================

@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    """
    Starts Playwright once for the complete test session.
    """

    logger.info("Initializing Playwright engine")

    with sync_playwright() as playwright:
        yield playwright

    logger.info("Playwright engine closed")


# ============================================================
# Browser Fixture
# ============================================================

@pytest.fixture(scope="session")
def browser(
    playwright_instance: Playwright,
    config: ConfigReader,
) -> Generator[Browser, None, None]:
    """
    Launches the configured browser once for the test session.
    """

    browser_name = config.get_browser()
    headless = config.is_headless()
    slow_mo = config.get_slow_mo()

    logger.info(
        "Launching browser: '%s' | Headless: %s | SlowMo: %sms",
        browser_name,
        headless,
        slow_mo,
    )

    # --------------------------------------------------------
    # Browser launch arguments
    # --------------------------------------------------------

    launch_args: list[str] = []

    # Start Chromium maximized when running in headed mode.
    if browser_name.lower() == "chromium" and not headless:
        launch_args.append("--start-maximized")

    # --------------------------------------------------------
    # Launch selected browser
    # --------------------------------------------------------

    if browser_name.lower() == "chromium":

        browser = playwright_instance.chromium.launch(
            headless=headless,
            slow_mo=slow_mo,
            args=launch_args,
        )

    elif browser_name.lower() == "firefox":

        browser = playwright_instance.firefox.launch(
            headless=headless,
            slow_mo=slow_mo,
            args=launch_args,
        )

    elif browser_name.lower() == "webkit":

        browser = playwright_instance.webkit.launch(
            headless=headless,
            slow_mo=slow_mo,
            args=launch_args,
        )

    else:
        raise ValueError(
            f"Unsupported browser: {browser_name}. "
            "Supported browsers: chromium, firefox, webkit"
        )

    # --------------------------------------------------------
    # Provide browser to tests
    # --------------------------------------------------------

    yield browser

    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------

    logger.info("Closing browser session")

    browser.close()


# ============================================================
# Browser Context Fixture
# ============================================================

@pytest.fixture
def context(
    browser: Browser,
) -> Generator[BrowserContext, None, None]:
    """
    Creates a fresh BrowserContext for every test.

    no_viewport=True allows the page to use the actual browser
    window size instead of forcing 1280x720.
    """

    headless = ConfigReader.is_headless()

    if headless:
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True,
        )
    else:
        context = browser.new_context(
            no_viewport=True,
            ignore_https_errors=True,
        )

    yield context

    logger.info("Closing BrowserContext")

    context.close()



# ============================================================
# Active Page Tracking
# ============================================================

_active_page: Page | None = None


# ============================================================
# Page Fixture
# ============================================================

@pytest.fixture
def page(
    context: BrowserContext,
) -> Generator[Page, None, None]:
    """
    Creates a fresh Playwright Page for every test.
    """

    global _active_page

    # --------------------------------------------------------
    # Create page
    # --------------------------------------------------------

    page = context.new_page()

    # --------------------------------------------------------
    # Configure Playwright timeouts
    # --------------------------------------------------------

    page.set_default_timeout(DEFAULT_TIMEOUT)

    page.set_default_navigation_timeout(
        DEFAULT_TIMEOUT
    )

    # --------------------------------------------------------
    # Track active page
    # --------------------------------------------------------

    _active_page = page

    logger.info(
        "Initialized new page with timeout %sms",
        DEFAULT_TIMEOUT,
    )

    # --------------------------------------------------------
    # Provide page to test
    # --------------------------------------------------------

    yield page

    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------

    _active_page = None

    if not page.is_closed():
        page.close()


# ============================================================
# Screenshot on Test Failure
# ============================================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[Any],
) -> Generator[None, None, None]:
    """
    Captures a full-page screenshot when a test fails
    and attaches it to the pytest HTML report.
    """

    outcome = yield

    report = outcome.get_result()

    # --------------------------------------------------------
    # Only capture screenshots for test execution failures
    # --------------------------------------------------------

    if report.when != "call":
        return

    if not report.failed:
        return

    global _active_page

    # --------------------------------------------------------
    # Check if a page is available
    # --------------------------------------------------------

    if _active_page is None:

        logger.warning(
            "Test failed but no active Playwright page "
            "was available for screenshot capture."
        )

        return

    if _active_page.is_closed():

        logger.warning(
            "Test failed but the Playwright page "
            "is already closed."
        )

        return

    # --------------------------------------------------------
    # Screenshot directory
    # --------------------------------------------------------

    screenshot_dir = Path("screenshots")

    screenshot_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Generate screenshot filename
    # --------------------------------------------------------

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    safe_test_name = (
        item.nodeid
        .replace("::", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        .replace(" ", "_")
    )

    screenshot_path = (
        screenshot_dir
        / f"{safe_test_name}_{timestamp}.png"
    )

    # --------------------------------------------------------
    # Capture screenshot
    # --------------------------------------------------------

    try:

        _active_page.screenshot(
            path=str(screenshot_path),
            full_page=True,
        )

        logger.error(
            "Test failed. Screenshot saved: %s",
            screenshot_path,
        )

        # ----------------------------------------------------
        # Attach screenshot to pytest-html
        # ----------------------------------------------------

        if hasattr(report, "extras"):

            with open(
                screenshot_path,
                "rb",
            ) as image_file:

                encoded_image = base64.b64encode(
                    image_file.read()
                ).decode("utf-8")

            report.extras.append(
                pytest_html.extras.image(
                    encoded_image,
                    mime_type="image/png",
                )
            )

    except Exception as screenshot_error:

        logger.error(
            "Failed to capture screenshot: %s",
            screenshot_error,
        )


# ============================================================
# Pytest HTML Report Title
# ============================================================

def pytest_html_report_title(
    report: Any,
) -> None:
    """
    Sets the title of the generated HTML report.
    """

    report.title = (
        "OrangeHRM Playwright BDD "
        "Automation Test Report"
    )


# ============================================================
# Pytest Configuration
# ============================================================

def pytest_configure(
    config: pytest.Config,
) -> None:
    """
    Creates required project directories before
    the test execution starts.
    """

    Path("reports").mkdir(
        parents=True,
        exist_ok=True,
    )

    Path("screenshots").mkdir(
        parents=True,
        exist_ok=True,
    )