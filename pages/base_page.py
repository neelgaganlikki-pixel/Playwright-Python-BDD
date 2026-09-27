from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from utils.logger import get_logger

logger = get_logger("BasePage")


class BasePage:
    """
    Base Page Object providing common locators, wait strategies, and interactions
    shared across all OrangeHRM pages.
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logger

        # Common Locators
        self.user_dropdown = page.locator(".oxd-userdropdown-tab")
        self.user_dropdown_name = page.locator(".oxd-userdropdown-name")
        self.logout_option = page.locator("a:has-text('Logout')")
        self.header_breadcrumb = page.locator(".oxd-topbar-header-breadcrumb")
        self.header_title = page.locator("h6.oxd-topbar-header-breadcrumb-module")
        self.toast_message = page.locator(".oxd-toast-content-text")
        self.toast_close = page.locator(".oxd-toast-close")

        # Side Navigation Menu Items
        self.menu_admin = page.locator("a[href*='viewAdminModule']")
        self.menu_pim = page.locator("a[href*='viewPimModule']")
        self.menu_leave = page.locator("a[href*='viewLeaveModule']")
        self.menu_time = page.locator("a[href*='viewTimeModule']")
        self.menu_recruitment = page.locator("a[href*='viewRecruitmentModule']")
        self.menu_dashboard = page.locator("a[href*='dashboard']")
        self.menu_buzz = page.locator("a[href*='viewBuzz']")

    def navigate(self, url: str) -> None:
        self.logger.info(f"Navigating to URL: {url}")
        self.page.goto(url, wait_until="domcontentloaded")

    def get_title(self) -> str:
        return self.page.title()

    def get_url(self) -> str:
        return self.page.url

    def get_header_text(self) -> str:
        self.header_breadcrumb.wait_for(state="visible", timeout=15000)
        return self.header_breadcrumb.inner_text().strip()

    def navigate_to_pim(self) -> None:
        self.logger.info("Navigating to PIM module")
        self.menu_pim.click()
        self.page.wait_for_load_state("domcontentloaded")

    def navigate_to_leave(self) -> None:
        self.logger.info("Navigating to Leave module")
        self.menu_leave.click()
        self.page.wait_for_load_state("domcontentloaded")

    def navigate_to_recruitment(self) -> None:
        self.logger.info("Navigating to Recruitment module")
        self.menu_recruitment.click()
        self.page.wait_for_load_state("domcontentloaded")

    def navigate_to_buzz(self) -> None:
        self.logger.info("Navigating to Buzz module")
        self.menu_buzz.click()
        self.page.wait_for_load_state("domcontentloaded")

    def navigate_to_dashboard(self) -> None:
        self.logger.info("Navigating to Dashboard module")
        self.menu_dashboard.click()
        self.page.wait_for_load_state("domcontentloaded")

    def logout(self) -> None:
        self.logger.info("Logging out of the application")
        self.user_dropdown.wait_for(state="visible", timeout=15000)
        self.user_dropdown.click()
        self.logout_option.wait_for(state="visible", timeout=10000)
        self.logout_option.click()
        self.page.wait_for_url("**/auth/login**", timeout=15000)

    def wait_for_toast(self, timeout: int = 10000) -> str:
        """
        Wait for OrangeHRM notification toast and return its message text.
        """
        try:
            self.toast_message.wait_for(state="visible", timeout=timeout)
            text = self.toast_message.inner_text().strip()
            self.logger.info(f"Toast notification appeared: '{text}'")
            return text
        except PlaywrightTimeoutError:
            self.logger.warning("Toast notification was not observed within timeout.")
            return ""
