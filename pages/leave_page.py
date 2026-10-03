from playwright.sync_api import Page
from pages.base_page import BasePage


class LeavePage(BasePage):
    """
    Page Object representing the OrangeHRM Leave module with self-healing.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Tabs
        self.tab_leave_list = page.locator("a:has-text('Leave List')")
        self.tab_apply = page.locator("a:has-text('Apply')")

        # Filters
        self.input_from_date = page.locator("div.oxd-input-group:has-text('From Date') input")
        self.input_to_date = page.locator("div.oxd-input-group:has-text('To Date') input")
        self.btn_search = page.locator("button[type='submit']:has-text('Search')")
        self.btn_reset = page.locator("button[type='reset']:has-text('Reset')")

        # Results area
        self.results_container = page.locator(".orangehrm-paper-container")
        self.records_span = page.locator(".orangehrm-paper-container .orangehrm-horizontal-padding span")

    def go_to_leave_list(self) -> None:
        self.logger.info("Opening Leave List tab")
        self.heal_click(
            element_name="Leave List Tab",
            primary="a:has-text('Leave List')",
            fallbacks=[
                "//a[contains(text(), 'Leave List')]",
                "li:has-text('Leave List') a",
                ".oxd-topbar-body-nav-tab:has-text('Leave List')",
            ],
            timeout=15000,
        )
        self.heal_wait_for(
            element_name="Leave Results Container",
            primary=".orangehrm-paper-container",
            fallbacks=[".oxd-table", ".oxd-table-filter", ".orangehrm-container"],
            timeout=20000,
        )

    def click_search(self) -> None:
        self.logger.info("Clicking Search on Leave List")
        self.heal_click(
            element_name="Leave Search Button",
            primary="button[type='submit']:has-text('Search')",
            fallbacks=[
                "button[type='submit']",
                "button.orangehrm-left-space",
                "//button[contains(., 'Search')]",
            ],
        )
        self.page.wait_for_load_state("networkidle")

    def click_reset(self) -> None:
        self.logger.info("Clicking Reset on Leave List")
        self.heal_click(
            element_name="Leave Reset Button",
            primary="button[type='reset']:has-text('Reset')",
            fallbacks=[
                "button[type='reset']",
                "button.oxd-button--ghost",
                "//button[contains(., 'Reset')]",
            ],
        )
        self.page.wait_for_load_state("networkidle")

    def is_leave_list_displayed(self, timeout: int = 15000) -> bool:
        visible = self.heal_is_visible(
            element_name="Leave Results Container",
            primary=".orangehrm-paper-container",
            fallbacks=[".oxd-table", ".oxd-table-filter", ".orangehrm-container"],
            timeout=timeout,
        )
        if visible:
            return True
        return "viewLeaveList" in self.page.url

    def get_records_text(self) -> str:
        try:
            text = self.heal_get_text(
                element_name="Leave Records Count Label",
                primary=".orangehrm-paper-container .orangehrm-horizontal-padding span",
                fallbacks=[
                    ".orangehrm-horizontal-padding span",
                    ".orangehrm-paper-container span",
                    "span.oxd-text--span:has-text('Record')",
                ],
                timeout=10000,
            )
            self.logger.info(f"Leave records status: {text}")
            return text
        except Exception:
            if self.results_container.is_visible():
                return self.results_container.inner_text()
            return ""

