from typing import Any, List, Optional
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError

from utils.logger import get_logger
from utils.self_healing import self_healing_engine

logger = get_logger("BasePage")


class BasePage:
    """
    Base Page Object providing common locators, wait strategies, and self-healing
    interactions shared across all OrangeHRM pages.
    """

    def __init__(self, page: Page):
        self.page = page
        self.logger = logger
        self.engine = self_healing_engine

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

    # =========================================================================
    # Self-Healing Action Helpers
    # =========================================================================

    def heal_click(
        self,
        element_name: str,
        primary: str,
        fallbacks: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Click an element with automatic self-healing across fallback candidates.
        """
        self.engine.execute_with_healing(
            page=self.page,
            page_name=self.__class__.__name__,
            element_name=element_name,
            primary_locator=primary,
            action_name="click",
            action_fn=lambda loc: loc.click(),
            fallbacks=fallbacks,
            timeout_ms=timeout,
        )

    def heal_fill(
        self,
        element_name: str,
        primary: str,
        text: str,
        fallbacks: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Fill an input element with automatic self-healing across fallback candidates.
        """
        def _fill_action(loc: Locator) -> None:
            loc.fill("")
            loc.fill(text)

        self.engine.execute_with_healing(
            page=self.page,
            page_name=self.__class__.__name__,
            element_name=element_name,
            primary_locator=primary,
            action_name="fill",
            action_fn=_fill_action,
            fallbacks=fallbacks,
            timeout_ms=timeout,
        )

    def heal_get_text(
        self,
        element_name: str,
        primary: str,
        fallbacks: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> str:
        """
        Fetch inner text from an element with automatic self-healing.
        """
        return self.engine.execute_with_healing(
            page=self.page,
            page_name=self.__class__.__name__,
            element_name=element_name,
            primary_locator=primary,
            action_name="inner_text",
            action_fn=lambda loc: loc.inner_text().strip(),
            fallbacks=fallbacks,
            timeout_ms=timeout,
        )

    def heal_is_visible(
        self,
        element_name: str,
        primary: str,
        fallbacks: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> bool:
        """
        Verify if an element is visible with automatic self-healing across fallback candidates.
        """
        timeout_val = timeout or 5000
        return self.engine.execute_with_healing(
            page=self.page,
            page_name=self.__class__.__name__,
            element_name=element_name,
            primary_locator=primary,
            action_name="is_visible",
            action_fn=lambda loc: loc.is_visible(),
            fallbacks=fallbacks,
            timeout_ms=timeout_val,
            is_query=True,
        )

    def heal_select_option(
        self,
        element_name: str,
        primary: str,
        value: str,
        fallbacks: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Select dropdown option with self-healing across fallback candidates.
        """
        self.engine.execute_with_healing(
            page=self.page,
            page_name=self.__class__.__name__,
            element_name=element_name,
            primary_locator=primary,
            action_name="select_option",
            action_fn=lambda loc: loc.select_option(value),
            fallbacks=fallbacks,
            timeout_ms=timeout,
        )

    def heal_wait_for(
        self,
        element_name: str,
        primary: str,
        state: str = "visible",
        fallbacks: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Wait for element state with self-healing across fallback candidates.
        """
        self.engine.execute_with_healing(
            page=self.page,
            page_name=self.__class__.__name__,
            element_name=element_name,
            primary_locator=primary,
            action_name=f"wait_for({state})",
            action_fn=lambda loc: loc.wait_for(state=state, timeout=timeout or 15000),
            fallbacks=fallbacks,
            timeout_ms=timeout,
        )

    # =========================================================================
    # Standard Page Navigation & Interactions
    # =========================================================================

    def navigate(self, url: str) -> None:
        self.logger.info(f"Navigating to URL: {url}")
        self.page.goto(url, wait_until="domcontentloaded")

    def get_title(self) -> str:
        return self.page.title()

    def get_url(self) -> str:
        return self.page.url

    def get_header_text(self) -> str:
        return self.heal_get_text(
            element_name="Header Breadcrumb",
            primary=".oxd-topbar-header-breadcrumb",
            fallbacks=[
                "h6.oxd-topbar-header-breadcrumb-module",
                ".oxd-topbar-header-title",
                "header .oxd-topbar-header-breadcrumb",
            ],
            timeout=15000,
        )

    def navigate_to_pim(self) -> None:
        self.logger.info("Navigating to PIM module")
        self.heal_click(
            element_name="PIM Navigation Menu",
            primary="a[href*='viewPimModule']",
            fallbacks=[
                "span:has-text('PIM')",
                "a:has-text('PIM')",
                "//span[text()='PIM']/..",
            ],
        )
        self.page.wait_for_load_state("domcontentloaded")

    def navigate_to_leave(self) -> None:
        self.logger.info("Navigating to Leave module")
        self.heal_click(
            element_name="Leave Navigation Menu",
            primary="a[href*='viewLeaveModule']",
            fallbacks=[
                "span:has-text('Leave')",
                "a:has-text('Leave')",
                "//span[text()='Leave']/..",
            ],
        )
        self.page.wait_for_load_state("domcontentloaded")

    def navigate_to_recruitment(self) -> None:
        self.logger.info("Navigating to Recruitment module")
        self.heal_click(
            element_name="Recruitment Navigation Menu",
            primary="a[href*='viewRecruitmentModule']",
            fallbacks=[
                "span:has-text('Recruitment')",
                "a:has-text('Recruitment')",
                "//span[text()='Recruitment']/..",
            ],
        )
        self.page.wait_for_load_state("domcontentloaded")

    def navigate_to_buzz(self) -> None:
        self.logger.info("Navigating to Buzz module")
        self.heal_click(
            element_name="Buzz Navigation Menu",
            primary="a[href*='viewBuzz']",
            fallbacks=[
                "span:has-text('Buzz')",
                "a:has-text('Buzz')",
                "//span[text()='Buzz']/..",
            ],
        )
        self.page.wait_for_load_state("domcontentloaded")

    def navigate_to_dashboard(self) -> None:
        self.logger.info("Navigating to Dashboard module")
        self.heal_click(
            element_name="Dashboard Navigation Menu",
            primary="a[href*='dashboard']",
            fallbacks=[
                "span:has-text('Dashboard')",
                "a:has-text('Dashboard')",
                "//span[text()='Dashboard']/..",
            ],
        )
        self.page.wait_for_load_state("domcontentloaded")

    def logout(self) -> None:
        self.logger.info("Logging out of the application")
        self.heal_click(
            element_name="User Profile Dropdown",
            primary=".oxd-userdropdown-tab",
            fallbacks=[
                "p.oxd-userdropdown-name",
                "img.oxd-userdropdown-img",
                ".oxd-userdropdown",
                "//li[@class='oxd-userdropdown']",
            ],
            timeout=15000,
        )
        self.heal_click(
            element_name="Logout Option",
            primary="a:has-text('Logout')",
            fallbacks=[
                "a[href*='logout']",
                "//a[contains(text(), 'Logout')]",
                "li:has-text('Logout') a",
                "role=menuitem >> text=Logout",
            ],
            timeout=10000,
        )
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

