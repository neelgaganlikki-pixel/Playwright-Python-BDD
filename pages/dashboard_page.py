from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage


class DashboardPage(BasePage):
    """
    Page Object representing the OrangeHRM Dashboard Page.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.dashboard_header = page.locator("h6.oxd-topbar-header-breadcrumb-module")
        self.widgets = page.locator(".orangehrm-dashboard-widget")
        self.quick_launch_cards = page.locator(".orangehrm-quick-launch-card")

    def is_dashboard_displayed(self, timeout: int = 15000) -> bool:
        try:
            self.dashboard_header.wait_for(state="visible", timeout=timeout)
            return "Dashboard" in self.dashboard_header.inner_text()
        except PlaywrightTimeoutError:
            return False

    def get_dashboard_header_text(self) -> str:
        self.dashboard_header.wait_for(state="visible", timeout=15000)
        return self.dashboard_header.inner_text().strip()

    def get_widgets_count(self) -> int:
        try:
            self.widgets.first.wait_for(state="visible", timeout=10000)
            return self.widgets.count()
        except PlaywrightTimeoutError:
            return 0
