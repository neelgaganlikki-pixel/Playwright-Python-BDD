from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage


class DashboardPage(BasePage):
    """
    Page Object representing the OrangeHRM Dashboard Page.
    """

    DASHBOARD_URL = "**/web/index.php/dashboard/index"

    def __init__(self, page: Page):
        super().__init__(page)

        self.dashboard_header = page.locator(
            "h6.oxd-topbar-header-breadcrumb-module"
        )

        self.widgets = page.locator(
            ".orangehrm-dashboard-widget"
        )

        self.quick_launch_cards = page.locator(
            ".orangehrm-quick-launch-card"
        )

    def is_dashboard_displayed(self, timeout: int = 15000) -> bool:
        """
        Verify that the user has successfully reached the Dashboard.
        URL validation is used as the primary check, followed by the
        Dashboard header when available.
        """

        try:
            # First wait for the Dashboard URL
            self.page.wait_for_url(
                self.DASHBOARD_URL,
                timeout=timeout
            )

            # URL is the strongest indication that login succeeded
            if "/web/index.php/dashboard/index" not in self.page.url:
                return False

            # Give the dashboard UI time to render
            try:
                self.dashboard_header.wait_for(
                    state="visible",
                    timeout=5000
                )

                header_text = self.dashboard_header.inner_text().strip()

                return "Dashboard" in header_text

            except PlaywrightTimeoutError:
                # URL is correct even if header rendering is delayed
                return True

        except PlaywrightTimeoutError:
            return False

    def get_dashboard_header_text(self) -> str:
        self.dashboard_header.wait_for(
            state="visible",
            timeout=15000
        )

        return self.dashboard_header.inner_text().strip()

    def get_widgets_count(self) -> int:
        try:
            self.widgets.first.wait_for(
                state="visible",
                timeout=10000
            )

            return self.widgets.count()

        except PlaywrightTimeoutError:
            return 0

    def logout(self):
        """
        Logout from OrangeHRM.
        """

        # Open user dropdown
        user_dropdown = self.page.locator(
            ".oxd-userdropdown-tab"
        )

        user_dropdown.wait_for(
            state="visible",
            timeout=10000
        )

        user_dropdown.click()

        # Click Logout
        logout_button = self.page.get_by_text(
            "Logout",
            exact=True
        )

        logout_button.wait_for(
            state="visible",
            timeout=10000
        )

        logout_button.click()

        # Verify login page
        self.page.wait_for_url(
            "**/web/index.php/auth/login",
            timeout=15000
        )

    def is_login_page_displayed(self) -> bool:

        try:
            self.page.wait_for_url(
                "**/web/index.php/auth/login",
                timeout=10000
            )

            return self.page.locator(
                "input[name='username']"
            ).is_visible()

        except PlaywrightTimeoutError:
            return False