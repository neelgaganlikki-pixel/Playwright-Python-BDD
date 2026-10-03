import re
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage


class EmployeePage(BasePage):
    """
    Page Object representing the OrangeHRM PIM / Employee Management module with self-healing.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation Subtabs
        self.tab_employee_list = page.locator("a:has-text('Employee List')")
        self.tab_add_employee = page.locator("a:has-text('Add Employee')")

        # Add Employee Locators
        self.btn_add = page.locator("button:has-text('Add'), a:has-text('Add Employee')").first
        self.input_first_name = page.locator("input[name='firstName']")
        self.input_middle_name = page.locator("input[name='middleName']")
        self.input_last_name = page.locator("input[name='lastName']")
        self.input_emp_id = page.locator("div.oxd-input-group:has-text('Employee Id') input")
        self.emp_id_error = page.locator("div.oxd-input-group:has-text('Employee Id') .oxd-input-group__message")
        self.btn_save = page.locator("button[type='submit']:has-text('Save')")
        self.personal_details_header = page.locator("h6:has-text('Personal Details')")

        # Employee Search Filter Locators
        self.filter_emp_id = page.locator("div.oxd-input-group:has-text('Employee Id') input")
        self.btn_search = page.locator("button[type='submit']:has-text('Search')")
        self.btn_reset = page.locator("button[type='reset']:has-text('Reset')")

        # Table Locators
        self.table_body = page.locator(".oxd-table-body")
        self.table_cards = page.locator(".oxd-table-body .oxd-table-card")
        self.records_found_label = page.locator(".orangehrm-horizontal-padding span")

    def go_to_add_employee(self) -> None:
        self.logger.info("Opening Add Employee tab")
        self.heal_click(
            element_name="Add Employee Button",
            primary="a:has-text('Add Employee')",
            fallbacks=[
                "button:has-text('Add')",
                "//a[contains(text(), 'Add Employee')]",
                "//button[contains(., 'Add')]",
                ".orangehrm-header-container button",
            ],
            timeout=20000,
        )
        self.heal_wait_for(
            element_name="Employee First Name Input",
            primary="input[name='firstName']",
            fallbacks=["input[placeholder='First Name']", ".orangehrm-firstname input"],
            timeout=20000,
        )

    def set_employee_id(self, emp_id: str) -> None:
        self.logger.info(f"Setting unique Employee ID: '{emp_id}'")
        self.heal_fill(
            element_name="Employee ID Field",
            primary="div.oxd-input-group:has-text('Employee Id') input",
            text=emp_id,
            fallbacks=[
                ".oxd-input-group:has(label:has-text('Employee Id')) input",
                "//label[contains(text(), 'Employee Id')]/ancestor::div[contains(@class, 'oxd-input-group')]//input",
            ],
            timeout=10000,
        )

    def go_to_employee_list(self) -> None:
        self.logger.info("Opening Employee List tab")
        self.heal_click(
            element_name="Employee List Tab",
            primary="a:has-text('Employee List')",
            fallbacks=[
                "//a[contains(text(), 'Employee List')]",
                "li:has-text('Employee List') a",
            ],
            timeout=15000,
        )
        self.heal_wait_for(
            element_name="Employee Records Table Body",
            primary=".oxd-table-body",
            state="attached",
            fallbacks=[".oxd-table", ".orangehrm-container"],
            timeout=20000,
        )

    def add_employee(self, first_name: str, last_name: str, middle_name: str = "", emp_id: str = None) -> str:
        self.logger.info(f"Adding employee: {first_name} {last_name}")
        self.heal_fill(
            element_name="First Name Input",
            primary="input[name='firstName']",
            text=first_name,
            fallbacks=["input[placeholder='First Name']", ".orangehrm-firstname input"],
        )
        if middle_name:
            self.heal_fill(
                element_name="Middle Name Input",
                primary="input[name='middleName']",
                text=middle_name,
                fallbacks=["input[placeholder='Middle Name']", ".orangehrm-middlename input"],
            )
        self.heal_fill(
            element_name="Last Name Input",
            primary="input[name='lastName']",
            text=last_name,
            fallbacks=["input[placeholder='Last Name']", ".orangehrm-lastname input"],
        )

        if emp_id:
            self.set_employee_id(emp_id)
            used_id = emp_id
        else:
            used_id = self.input_emp_id.input_value()

        self.heal_click(
            element_name="Save Employee Button",
            primary="button[type='submit']:has-text('Save')",
            fallbacks=[
                "button[type='submit']",
                "button.oxd-button--secondary",
                "//button[contains(., 'Save')]",
            ],
        )
        self.page.wait_for_selector(".oxd-toast, h6:has-text('Personal Details')", timeout=20000)
        self.logger.info(f"Employee saved with ID: {used_id}")
        return used_id

    def is_personal_details_displayed(self, timeout: int = 15000) -> bool:
        header_visible = self.heal_is_visible(
            element_name="Personal Details Header",
            primary="h6:has-text('Personal Details')",
            fallbacks=[
                ".orangehrm-edit-employee-content",
                "h6.orangehrm-main-title",
                "a:has-text('Personal Details')",
            ],
            timeout=timeout,
        )
        if header_visible:
            return True
        return "viewPersonalDetails" in self.page.url

    def get_first_employee_id_from_list(self, timeout: int = 20000) -> str:
        self.table_cards.first.wait_for(state="visible", timeout=timeout)
        first_card = self.table_cards.first
        cells = first_card.locator(".oxd-table-cell")
        if cells.count() > 1:
            emp_id = cells.nth(1).inner_text().strip()
        else:
            card_text = first_card.inner_text()
            match = re.search(r"Id\s*(\w+)", card_text, re.IGNORECASE)
            emp_id = match.group(1).strip() if match else card_text.split()[0].strip()
        self.logger.info(f"Retrieved first employee ID: '{emp_id}'")
        return emp_id

    def search_by_employee_id(self, emp_id: str) -> None:
        self.logger.info(f"Searching employee by ID: '{emp_id}'")
        if not self.filter_emp_id.is_visible():
            filter_header = self.page.locator(".oxd-table-filter-header")
            if filter_header.is_visible():
                filter_header.click()

        self.heal_fill(
            element_name="Employee Search Filter Input",
            primary="div.oxd-input-group:has-text('Employee Id') input",
            text=emp_id,
            fallbacks=[
                ".oxd-table-filter input",
                "//label[contains(text(), 'Employee Id')]/ancestor::div[contains(@class, 'oxd-input-group')]//input",
            ],
            timeout=15000,
        )
        self.heal_click(
            element_name="Search Filter Submit Button",
            primary="button[type='submit']:has-text('Search')",
            fallbacks=[
                "button[type='submit']",
                "button.orangehrm-left-space",
                "//button[contains(., 'Search')]",
            ],
        )
        self.page.wait_for_load_state("networkidle")

    def get_search_results_count(self) -> int:
        try:
            self.table_cards.first.wait_for(state="visible", timeout=10000)
            return self.table_cards.count()
        except PlaywrightTimeoutError:
            return 0

    def is_employee_id_present_in_results(self, emp_id: str) -> bool:
        count = self.get_search_results_count()
        if count == 0:
            return False
        for i in range(count):
            card_text = self.table_cards.nth(i).inner_text()
            if emp_id in card_text:
                return True
        return False

