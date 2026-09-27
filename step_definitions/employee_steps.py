from pytest_bdd import when, then
from playwright.sync_api import Page
from pages.employee_page import EmployeePage
from utils.test_data import TestDataGenerator
from utils.logger import get_logger

logger = get_logger("EmployeeSteps")


@when("the user navigates to the PIM module")
def navigate_to_pim(page: Page):
    emp_page = EmployeePage(page)
    emp_page.navigate_to_pim()


@when("clicks on the Add Employee tab")
def click_add_employee_tab(page: Page):
    emp_page = EmployeePage(page)
    emp_page.go_to_add_employee()


@when("provides valid employee details")
def provide_employee_details(page: Page, test_context: dict):
    first_name, middle_name, last_name = TestDataGenerator.generate_employee_name()
    test_context["first_name"] = first_name
    test_context["middle_name"] = middle_name
    test_context["last_name"] = last_name

    emp_page = EmployeePage(page)
    emp_page.input_first_name.fill(first_name)
    emp_page.input_middle_name.fill(middle_name)
    emp_page.input_last_name.fill(last_name)
    test_context["emp_id"] = emp_page.input_emp_id.input_value()


@when("saves the employee")
def save_employee(page: Page):
    emp_page = EmployeePage(page)
    emp_page.btn_save.click()
    page.wait_for_selector(".oxd-toast, h6:has-text('Personal Details')", timeout=20000)


@then("the employee personal details page should be displayed")
def verify_personal_details_page(page: Page):
    emp_page = EmployeePage(page)
    assert emp_page.is_personal_details_displayed(), "Personal details section was not displayed."


@when("retrieves an existing employee ID from the list")
def retrieve_existing_employee_id(page: Page, test_context: dict):
    emp_page = EmployeePage(page)
    emp_id = emp_page.get_first_employee_id_from_list()
    test_context["search_emp_id"] = emp_id


@when("searches for the employee using that ID")
def search_employee_by_id(page: Page, test_context: dict):
    emp_page = EmployeePage(page)
    emp_id = test_context["search_emp_id"]
    emp_page.search_by_employee_id(emp_id)


@then("the employee record should be displayed in the results table")
def verify_employee_search_results(page: Page, test_context: dict):
    emp_page = EmployeePage(page)
    emp_id = test_context["search_emp_id"]
    assert emp_page.is_employee_id_present_in_results(emp_id), (
        f"Employee ID '{emp_id}' not found in search results."
    )
