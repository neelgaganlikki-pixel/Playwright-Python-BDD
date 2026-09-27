from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage


class RecruitmentPage(BasePage):
    """
    Page Object representing the OrangeHRM Recruitment module.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Tabs
        self.tab_candidates = page.locator("a:has-text('Candidates')")
        self.tab_vacancies = page.locator("a:has-text('Vacancies')")

        # Candidate List
        self.btn_add = page.locator("button:has-text('Add')")
        self.table_cards = page.locator(".oxd-table-body .oxd-table-card")
        self.candidates_count_label = page.locator(".orangehrm-horizontal-padding span")

        # Add Candidate Form
        self.input_first_name = page.locator("input[name='firstName']")
        self.input_middle_name = page.locator("input[name='middleName']")
        self.input_last_name = page.locator("input[name='lastName']")
        self.input_email = page.locator("div.oxd-input-group:has-text('Email') input")
        self.input_contact = page.locator("div.oxd-input-group:has-text('Contact Number') input")
        self.btn_save = page.locator("button[type='submit']:has-text('Save')")
        self.application_stage_header = page.locator("h6:has-text('Application Stage')")

    def go_to_candidates(self) -> None:
        self.logger.info("Opening Candidates tab in Recruitment")
        self.tab_candidates.click()
        self.btn_add.wait_for(state="visible", timeout=20000)

    def click_add_candidate(self) -> None:
        self.logger.info("Clicking Add Candidate button")
        self.btn_add.click()
        self.input_first_name.wait_for(state="visible", timeout=20000)

    def fill_candidate_info(
        self, first_name: str, last_name: str, email: str, contact_number: str = ""
    ) -> None:
        self.logger.info(f"Filling candidate info: {first_name} {last_name}, {email}")
        self.input_first_name.fill(first_name)
        self.input_last_name.fill(last_name)
        self.input_email.fill(email)
        if contact_number:
            self.input_contact.fill(contact_number)

    def save_candidate(self) -> None:
        self.logger.info("Saving candidate")
        self.btn_save.click()
        self.page.wait_for_selector(".oxd-toast, h6:has-text('Application Stage')", timeout=20000)

    def is_candidate_saved(self, timeout: int = 15000) -> bool:
        try:
            self.application_stage_header.wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return "addCandidate" in self.page.url or "viewCandidates" in self.page.url

    def get_candidates_count(self) -> int:
        try:
            self.table_cards.first.wait_for(state="visible", timeout=15000)
            return self.table_cards.count()
        except PlaywrightTimeoutError:
            return 0
