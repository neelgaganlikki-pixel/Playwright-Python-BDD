from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage


class EmployeePage(BasePage):
    """
    Page Object representing the OrangeHRM PIM / Employee Management module.
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
        self.tab_add_employee.click()
        self.input_first_name.wait_for(state="visible", timeout=20000)

    def go_to_employee_list(self) -> None:
        self.logger.info("Opening Employee List tab")
        self.tab_employee_list.click()
        self.table_body.wait_for(state="attached", timeout=20000)

    def add_employee(self, first_name: str, last_name: str, middle_name: str = "", emp_id: str = None) -> str:
        self.logger.info(f"Adding employee: {first_name} {last_name}")
        self.input_first_name.fill(first_name)
        if middle_name:
            self.input_middle_name.fill(middle_name)
        self.input_last_name.fill(last_name)

        if emp_id:
            self.input_emp_id.fill("")
            self.input_emp_id.fill(emp_id)
            used_id = emp_id
        else:
            used_id = self.input_emp_id.input_value()

        self.btn_save.click()
        self.page.wait_for_selector(".oxd-toast, h6:has-text('Personal Details')", timeout=20000)
        self.logger.info(f"Employee saved with ID: {used_id}")
        return used_id

    def is_personal_details_displayed(self, timeout: int = 15000) -> bool:
        try:
            self.personal_details_header.wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return "viewPersonalDetails" in self.page.url

    def get_first_employee_id_from_list(self, timeout: int = 20000) -> str:
        self.table_cards.first.wait_for(state="visible", timeout=timeout)
        # ID is usually in the 2nd cell (index 1)
        first_card = self.table_cards.first
        emp_id = first_card.locator(".oxd-table-cell").nth(1).inner_text().strip()
        self.logger.info(f"Retrieved first employee ID: {emp_id}")
        return emp_id

    def search_by_employee_id(self, emp_id: str) -> None:
        self.logger.info(f"Searching employee by ID: {emp_id}")
        self.filter_emp_id.wait_for(state="visible", timeout=15000)
        self.filter_emp_id.fill("")
        self.filter_emp_id.fill(emp_id)
        self.btn_search.click()
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
