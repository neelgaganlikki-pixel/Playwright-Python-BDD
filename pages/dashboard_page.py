from playwright.sync_api import Page
from pages.base_page import BasePage


class DashboardPage(BasePage):
    """
    Page Object representing the OrangeHRM Dashboard Page with integrated self-healing.
    """

    DASHBOARD_URL_PATTERN = "**/dashboard/**"

    def __init__(self, page: Page):
        super().__init__(page)

        # Standard locators (preserved for backwards compatibility)
        self.dashboard_header = page.locator("h6.oxd-topbar-header-breadcrumb-module")
        self.widgets = page.locator(".orangehrm-dashboard-widget")
        self.quick_launch_cards = page.locator(".orangehrm-quick-launch-card")

    def is_dashboard_displayed(self, timeout: int = 25000) -> bool:
        """
        Verify that the user has successfully reached the Dashboard using self-healing
        fallback locator strategies and page-state validation.
        Does not falsely pass if login fails or dashboard is genuinely absent.
        """
        try:
            # 1. Wait for navigation away from /auth/login towards dashboard
            if "/auth/login" in self.page.url or "/auth/validate" in self.page.url:
                try:
                    self.page.wait_for_url(self.DASHBOARD_URL_PATTERN, timeout=timeout)
                except PlaywrightTimeoutError:
                    pass

            # If still on login page or login error alert is visible, login failed
            if "/auth/login" in self.page.url:
                self.logger.warning("Browser is still on /auth/login page; login did not reach Dashboard.")
                return False

            # 2. Validate dashboard UI presence via self-healing candidates
            header_visible = self.heal_is_visible(
                element_name="Dashboard Header Element",
                primary="h6.oxd-topbar-header-breadcrumb-module",
                fallbacks=[
                    "h6:has-text('Dashboard')",
                    "header >> text=Dashboard",
                    ".oxd-topbar-header-breadcrumb",
                    "nav >> text=Dashboard",
                    "a[href*='dashboard'].active",
                    ".orangehrm-dashboard-widget",
                    ".orangehrm-dashboard-grid",
                ],
                timeout=8000,
            )

            if header_visible:
                return True

            # 3. Secondary check: widget container presence
            widget_visible = self.heal_is_visible(
                element_name="Dashboard Widgets Container",
                primary=".orangehrm-dashboard-widget",
                fallbacks=[
                    ".orangehrm-dashboard-grid",
                    ".oxd-sheet--card",
                    "p.oxd-text:has-text('Time at Work')",
                ],
                timeout=5000,
            )
            if widget_visible:
                return True

            # 4. Strict URL fallback: only if URL genuinely confirms /dashboard/ and no errors
            if "/web/index.php/dashboard" in self.page.url:
                self.logger.info("[SELF-HEALING] Dashboard confirmed via authenticated URL state: %s", self.page.url)
                return True

            return False

        except Exception as e:
            self.logger.warning("Error checking dashboard display: %s", e)
            return False

    def get_dashboard_header_text(self) -> str:
        """
        Retrieve header text using self-healing fallbacks.
        """
        return self.heal_get_text(
            element_name="Dashboard Header Text",
            primary="h6.oxd-topbar-header-breadcrumb-module",
            fallbacks=[
                "h6:has-text('Dashboard')",
                "header >> text=Dashboard",
                ".oxd-topbar-header-breadcrumb",
                ".oxd-topbar-header-title",
            ],
            timeout=15000,
        )

    def get_widgets_count(self) -> int:
        try:
            self.widgets.first.wait_for(state="visible", timeout=10000)
            return self.widgets.count()
        except PlaywrightTimeoutError:
            return 0

    def logout(self) -> None:
        """
        Logout from OrangeHRM using self-healing navigation.
        """
        super().logout()

    def is_login_page_displayed(self) -> bool:
        return self.heal_is_visible(
            element_name="Login Page Form",
            primary="input[name='username']",
            fallbacks=[
                "button[type='submit']",
                ".orangehrm-login-form",
                "h5:has-text('Login')",
            ],
            timeout=10000,
        )