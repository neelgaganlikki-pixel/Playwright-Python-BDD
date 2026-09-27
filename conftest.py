import base64
from datetime import datetime
from pathlib import Path
import pytest
from pytest_html import extras as html_extras
from playwright.sync_api import sync_playwright, Playwright, Browser, BrowserContext, Page

from config.config_reader import ConfigReader
from utils.logger import get_logger

logger = get_logger("Conftest")

# Global registration of all step definition modules for pytest-bdd
pytest_plugins = [
    "step_definitions.login_steps",
    "step_definitions.employee_steps",
    "step_definitions.leave_steps",
    "step_definitions.recruitment_steps",
    "step_definitions.buzz_steps",
]


@pytest.fixture(scope="session")
def config():
    """Provides access to framework configuration."""
    return ConfigReader


@pytest.fixture(scope="function")
def test_context() -> dict:
    """Dictionary to share state between Given-When-Then steps of a scenario."""
    return {}


@pytest.fixture(scope="session")
def playwright_instance():
    """Session-scoped Playwright instance."""
    logger.info("Initializing Playwright engine")
    with sync_playwright() as playwright:
        yield playwright
    logger.info("Playwright engine closed")


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Browser:
    """
    Session-scoped Browser instance launched according to configuration.
    Supports chromium, firefox, webkit, headless mode, and slow_mo.
    """
    browser_name = ConfigReader.get_browser()
    headless = ConfigReader.is_headless()
    slow_mo = ConfigReader.get_slow_mo()

    logger.info(
        f"Launching browser: '{browser_name}' | Headless: {headless} | SlowMo: {slow_mo}ms"
    )

    if browser_name == "firefox":
        browser_type = playwright_instance.firefox
    elif browser_name == "webkit":
        browser_type = playwright_instance.webkit
    else:
        browser_type = playwright_instance.chromium

    browser = browser_type.launch(
        headless=headless,
        slow_mo=slow_mo,
        args=["--start-maximized"] if not headless else [],
    )
    yield browser
    logger.info("Closing browser session")
    browser.close()


@pytest.fixture(scope="function")
def context(browser: Browser) -> BrowserContext:
    """
    Function-scoped fresh BrowserContext for each scenario to ensure strict isolation.
    """
    logger.info("Creating fresh BrowserContext")
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        ignore_https_errors=True,
    )
    yield context
    logger.info("Closing BrowserContext")
    context.close()


_active_page: Page | None = None


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    """
    Function-scoped fresh Page instance configured with default timeout.
    """
    global _active_page
    p = context.new_page()
    default_timeout = ConfigReader.get_default_timeout()
    p.set_default_timeout(default_timeout)
    p.set_default_navigation_timeout(default_timeout)
    _active_page = p

    logger.info(f"Initialized new page with timeout {default_timeout}ms")
    yield p
    _active_page = None
    p.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture a screenshot when a scenario step or test fails,
    save it to the screenshots directory, and embed it into the pytest-html report.
    """
    outcome = yield
    report = outcome.get_result()
    extras = getattr(report, "extras", [])

    if report.when == "call" and report.failed:
        # Check if page fixture is present in test arguments or global tracker
        page_instance = item.funcargs.get("page") or _active_page
        if page_instance and not page_instance.is_closed():
            try:
                screenshots_dir = Path(__file__).resolve().parent / "screenshots"
                screenshots_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                sanitized_name = item.name.replace("[", "_").replace("]", "_").replace(" ", "_")
                file_name = f"FAILED_{sanitized_name}_{timestamp}.png"
                file_path = screenshots_dir / file_name

                # Save file to disk
                screenshot_bytes = page_instance.screenshot(path=str(file_path), full_page=True)
                logger.error(f"Captured failure screenshot: {file_path}")

                # Embed into HTML report
                encoded_screenshot = base64.b64encode(screenshot_bytes).decode("ascii")
                extras.append(html_extras.png(encoded_screenshot, name="Failure Screenshot"))
            except Exception as e:
                logger.warning(f"Failed to capture screenshot on failure: {e}")

    report.extras = extras


def pytest_html_report_title(report):
    """Custom title for HTML test report."""
    report.title = "OrangeHRM UI Automation Report (Playwright + Pytest-BDD)"


def pytest_configure(config):
    """Configure custom metadata for pytest HTML report."""
    # Ensure reports and screenshots directories exist
    reports_dir = Path(__file__).resolve().parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir = Path(__file__).resolve().parent / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
