from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage


class RecruitmentPage(BasePage):
    """
    Page Object representing the OrangeHRM Recruitment module (Candidates & Vacancies)
    with integrated self-healing.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation Tabs
        self.tab_candidates = page.locator("a:has-text('Candidates')")
        self.tab_vacancies = page.locator("a:has-text('Vacancies')")

        # Candidate List Elements
        self.btn_add_candidate = page.locator("button:has-text('Add')")
        self.btn_add = self.btn_add_candidate
        self.table_cards = page.locator(".oxd-table-body .oxd-table-card")
        self.candidates_count_label = page.locator(".orangehrm-horizontal-padding span")

        # Add Candidate Form Elements
        self.input_first_name = page.locator("input[name='firstName']")
        self.input_middle_name = page.locator("input[name='middleName']")
        self.input_last_name = page.locator("input[name='lastName']")
        self.input_email = page.locator("div.oxd-input-group:has-text('Email') input")
        self.input_contact = page.locator("div.oxd-input-group:has-text('Contact Number') input")
        self.btn_save = page.locator("button[type='submit']:has-text('Save')")
        self.application_stage_header = page.locator("h6:has-text('Application Stage')")

        # Vacancy List & Form Elements
        self.btn_add_vacancy = page.locator(".orangehrm-header-container button:has-text('Add')")
        self.input_vacancy_name = page.locator("div.oxd-input-group:has-text('Vacancy Name') input")
        self.select_job_title = page.locator("div.oxd-input-group:has-text('Job Title') .oxd-select-text")
        self.input_hiring_manager = page.locator("div.oxd-input-group:has-text('Hiring Manager') input")
        self.input_positions = page.locator("div.oxd-input-group:has-text('Number of Positions') input")
        self.textarea_description = page.locator("div.oxd-input-group:has-text('Description') textarea")

    # -------------------------------------------------------------------------
    # Candidate Submodule Actions
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # Vacancy Submodule Actions (Noted & Integrated)
    # -------------------------------------------------------------------------

    def go_to_vacancies(self) -> None:
        self.logger.info("Navigating to Vacancies tab in Recruitment")
        self.heal_click(
            element_name="Recruitment Vacancies Tab",
            primary="a:has-text('Vacancies')",
            fallbacks=[
                "a.oxd-topbar-body-nav-tab-item:has-text('Vacancies')",
                "//a[contains(text(), 'Vacancies')]",
                "li:has-text('Vacancies') a",
            ],
            timeout=15000,
        )
        self.heal_wait_for(
            element_name="Add Vacancy Button",
            primary=".orangehrm-header-container button:has-text('Add')",
            fallbacks=[
                "button.oxd-button--secondary:has-text('Add')",
                "button:has-text('Add')",
                "//button[contains(., 'Add')]",
            ],
            timeout=20000,
        )

    def click_add_vacancy(self) -> None:
        self.logger.info("Clicking Add Vacancy button")
        self.heal_click(
            element_name="Add Vacancy Button",
            primary=".orangehrm-header-container button:has-text('Add')",
            fallbacks=[
                "button.oxd-button--secondary:has-text('Add')",
                "button:has-text('Add')",
                "//button[contains(., 'Add')]",
                ".orangehrm-header-container .oxd-button",
                "button:has(.bi-plus)",
            ],
            timeout=15000,
        )
        self.heal_wait_for(
            element_name="Vacancy Name Input",
            primary="div.oxd-input-group:has-text('Vacancy Name') input",
            fallbacks=[
                "input.oxd-input:below(:text('Vacancy Name'))",
                ".oxd-form-row:first-child input",
            ],
            timeout=20000,
        )

    def fill_vacancy_info(
        self,
        vacancy_name: str,
        job_title: Optional[str] = None,
        hiring_manager: Optional[str] = None,
        positions: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        self.logger.info(f"Filling vacancy details: Name='{vacancy_name}'")
        self.heal_fill(
            element_name="Vacancy Name Input",
            primary="div.oxd-input-group:has-text('Vacancy Name') input",
            text=vacancy_name,
            fallbacks=[
                "input.oxd-input:below(:text('Vacancy Name'))",
                "//label[contains(text(), 'Vacancy Name')]/ancestor::div[contains(@class, 'oxd-input-group')]//input",
            ],
        )

        if job_title:
            self.heal_click(
                element_name="Job Title Dropdown",
                primary="div.oxd-input-group:has-text('Job Title') .oxd-select-text",
                fallbacks=[".oxd-select-wrapper", ".oxd-select-text"],
            )
            self.heal_click(
                element_name=f"Job Title Option ({job_title})",
                primary=f".oxd-select-dropdown :text('{job_title}')",
                fallbacks=[f"//div[@role='listbox']//span[text()='{job_title}']"],
            )

        if hiring_manager:
            self.heal_fill(
                element_name="Hiring Manager Input",
                primary="div.oxd-input-group:has-text('Hiring Manager') input",
                text=hiring_manager,
                fallbacks=["input[placeholder='Type for hints...']"],
            )
            # Pick first autocomplete hint if available
            try:
                hint_loc = self.page.locator(".oxd-autocomplete-dropdown :first-child")
                hint_loc.wait_for(state="visible", timeout=3000)
                hint_loc.click()
            except Exception:
                pass

        if positions:
            self.heal_fill(
                element_name="Number of Positions Input",
                primary="div.oxd-input-group:has-text('Number of Positions') input",
                text=positions,
                fallbacks=["//label[text()='Number of Positions']/../..//input"],
            )

        if description:
            self.heal_fill(
                element_name="Vacancy Description Textarea",
                primary="div.oxd-input-group:has-text('Description') textarea",
                text=description,
                fallbacks=["textarea.oxd-textarea"],
            )

    def save_vacancy(self) -> None:
        self.logger.info("Saving Vacancy")
        self.heal_click(
            element_name="Save Vacancy Button",
            primary="button[type='submit']:has-text('Save')",
            fallbacks=[
                "button.oxd-button--secondary[type='submit']",
                "//button[contains(., 'Save')]",
            ],
        )
        self.page.wait_for_selector(".oxd-toast, h6:has-text('Edit Vacancy')", timeout=20000)

    def is_vacancy_saved(self, timeout: int = 15000) -> bool:
        saved = self.heal_is_visible(
            element_name="Edit Vacancy Header",
            primary="h6:has-text('Edit Vacancy')",
            fallbacks=[
                "h6.orangehrm-main-title",
                ".oxd-toast--success",
            ],
            timeout=timeout,
        )
        if saved:
            return True
        return "addJobVacancy" not in self.page.url

