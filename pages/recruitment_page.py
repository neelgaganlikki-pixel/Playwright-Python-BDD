from playwright.sync_api import Page
from pages.base_page import BasePage


class RecruitmentPage(BasePage):
    """
    Page Object representing the OrangeHRM Recruitment module with self-healing.
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
        self.heal_click(
            element_name="Recruitment Candidates Tab",
            primary="a:has-text('Candidates')",
            fallbacks=[
                "//a[contains(text(), 'Candidates')]",
                "li:has-text('Candidates') a",
                ".oxd-topbar-body-nav-tab:has-text('Candidates')",
            ],
            timeout=15000,
        )
        self.heal_wait_for(
            element_name="Add Candidate Button",
            primary="button:has-text('Add')",
            fallbacks=[
                ".orangehrm-header-container button",
                "//button[contains(., 'Add')]",
                "button.oxd-button--secondary",
            ],
            timeout=20000,
        )

    def click_add_candidate(self) -> None:
        self.logger.info("Clicking Add Candidate button")
        self.heal_click(
            element_name="Add Candidate Button",
            primary="button:has-text('Add')",
            fallbacks=[
                ".orangehrm-header-container button",
                "//button[contains(., 'Add')]",
                "button.oxd-button--secondary",
            ],
            timeout=20000,
        )
        self.heal_wait_for(
            element_name="Candidate First Name Input",
            primary="input[name='firstName']",
            fallbacks=["input[placeholder='First Name']", ".orangehrm-firstname input"],
            timeout=20000,
        )

    def fill_candidate_info(
        self, first_name: str, last_name: str, email: str, contact_number: str = ""
    ) -> None:
        self.logger.info(f"Filling candidate info: {first_name} {last_name}, {email}")
        self.heal_fill(
            element_name="Candidate First Name",
            primary="input[name='firstName']",
            text=first_name,
            fallbacks=["input[placeholder='First Name']", ".orangehrm-firstname input"],
        )
        self.heal_fill(
            element_name="Candidate Last Name",
            primary="input[name='lastName']",
            text=last_name,
            fallbacks=["input[placeholder='Last Name']", ".orangehrm-lastname input"],
        )
        self.heal_fill(
            element_name="Candidate Email",
            primary="div.oxd-input-group:has-text('Email') input",
            text=email,
            fallbacks=[
                ".oxd-input-group:has(label:has-text('Email')) input",
                "//label[contains(text(), 'Email')]/ancestor::div[contains(@class, 'oxd-input-group')]//input",
                "input[placeholder='Type here']",
            ],
        )
        if contact_number:
            self.heal_fill(
                element_name="Candidate Contact Number",
                primary="div.oxd-input-group:has-text('Contact Number') input",
                text=contact_number,
                fallbacks=[
                    ".oxd-input-group:has(label:has-text('Contact Number')) input",
                    "//label[contains(text(), 'Contact Number')]/ancestor::div[contains(@class, 'oxd-input-group')]//input",
                ],
            )

    def save_candidate(self) -> None:
        self.logger.info("Saving candidate")
        self.heal_click(
            element_name="Save Candidate Button",
            primary="button[type='submit']:has-text('Save')",
            fallbacks=[
                "button[type='submit']",
                "button.oxd-button--secondary",
                "//button[contains(., 'Save')]",
            ],
        )
        self.page.wait_for_selector(".oxd-toast, h6:has-text('Application Stage')", timeout=20000)

    def is_candidate_saved(self, timeout: int = 15000) -> bool:
        saved = self.heal_is_visible(
            element_name="Application Stage Header",
            primary="h6:has-text('Application Stage')",
            fallbacks=[
                ".orangehrm-recruitment-status",
                "h6.orangehrm-main-title",
                "//h6[contains(., 'Application Stage')]",
            ],
            timeout=timeout,
        )
        if saved:
            return True
        return "addCandidate" in self.page.url or "viewCandidates" in self.page.url

    def get_candidates_count(self) -> int:
        try:
            self.table_cards.first.wait_for(state="visible", timeout=15000)
            return self.table_cards.count()
        except PlaywrightTimeoutError:
            return 0

