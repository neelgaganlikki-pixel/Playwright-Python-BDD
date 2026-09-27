from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage


class LeavePage(BasePage):
    """
    Page Object representing the OrangeHRM Leave module.
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
        self.tab_leave_list.click()
        self.results_container.wait_for(state="visible", timeout=20000)

    def click_search(self) -> None:
        self.logger.info("Clicking Search on Leave List")
        self.btn_search.click()
        self.page.wait_for_load_state("networkidle")

    def click_reset(self) -> None:
        self.logger.info("Clicking Reset on Leave List")
        self.btn_reset.click()
        self.page.wait_for_load_state("networkidle")

    def is_leave_list_displayed(self, timeout: int = 15000) -> bool:
        try:
            self.results_container.wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return "viewLeaveList" in self.page.url

    def get_records_text(self) -> str:
        try:
            self.records_span.wait_for(state="visible", timeout=10000)
            text = self.records_span.inner_text().strip()
            self.logger.info(f"Leave records status: {text}")
            return text
        except PlaywrightTimeoutError:
            # Fall back to checking entire paper container text
            if self.results_container.is_visible():
                return self.results_container.inner_text()
            return ""
