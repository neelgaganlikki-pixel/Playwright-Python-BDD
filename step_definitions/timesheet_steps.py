import random
import time
from pytest_bdd import given, when, then, parsers
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.employee_page import EmployeePage
from pages.timesheet_page import TimesheetPage
from config.config_reader import ConfigReader
from utils.logger import get_logger
from utils.data_recorder import DataRecorder

logger = get_logger("TimesheetSteps")


def _do_login(page: Page, username: str, password: str) -> None:
    """Helper to perform full login and wait until dashboard is fully idle."""
    logger.info("Executing login for user: %s", username)
    login_page = LoginPage(page)
    login_page.login(username, password)
    page.wait_for_url("**/dashboard/**", timeout=25000)
    page.wait_for_load_state("networkidle")


def _do_logout(page: Page) -> None:
    """Helper to perform full logout and wait until login page is fully idle."""
    logger.info("Executing logout...")
    login_page = LoginPage(page)
    login_page.logout()
    page.wait_for_url("**/auth/login**", timeout=20000)
    page.wait_for_load_state("networkidle")


@given("an employee is registered with a reporting supervisor")
def register_employee_with_supervisor(page: Page, test_context: dict):
    """
    Dynamically registers a new employee with ESS login credentials and assigns
    the logged-in Admin as their direct supervisor in OrangeHRM PIM.
    """
    logger.info("[STEP] Given an employee is registered with a reporting supervisor")
    dashboard_page = DashboardPage(page)

    # 1. Ensure logged in as Admin supervisor
    if not dashboard_page.is_dashboard_displayed():
        _do_login(page, ConfigReader.get_username(), ConfigReader.get_password())

    # Ensure Time module is enabled across the application
    timesheet_page = TimesheetPage(page)
    timesheet_page.ensure_time_module_enabled()

    # Retrieve Admin supervisor full name
    admin_name = page.locator(".oxd-userdropdown-name").inner_text().strip()
    admin_first_token = admin_name.split()[0]
    logger.info("Active supervisor admin name: '%s' (filter token: '%s')", admin_name, admin_first_token)

    # 2. Add Employee with ESS Login Details
    base_url = ConfigReader.get_base_url().rstrip("/")
    emp_page = EmployeePage(page)
    emp_page.navigate_to_pim()
    emp_page.go_to_add_employee()

    ts = int(time.time()) % 100000
    emp_id = str(random.randint(800000, 999999))
    first_name = f"TimeF{ts}"
    last_name = f"TimeL{ts}"
    emp_user = f"user{ts}{random.randint(10, 99)}"
    emp_pass = "Password123!"

    logger.info(
        "Creating new employee: %s %s (EmpId: %s, User: %s)",
        first_name,
        last_name,
        emp_id,
        emp_user,
    )

    page.locator("input[name='firstName']").fill(first_name)
    page.locator("input[name='lastName']").fill(last_name)

    # Overwrite default Employee ID
    id_input = page.locator("div.oxd-input-group:has-text('Employee Id') input")
    id_input.fill("")
    id_input.fill(emp_id)

    # Enable "Create Login Details" toggle
    page.locator(".oxd-switch-input").click()
    page.wait_for_selector("div.oxd-input-group:has-text('Username') input", state="visible", timeout=10000)

    page.locator("div.oxd-input-group:has-text('Username') input").fill(emp_user)
    page.locator("div.oxd-input-group:has-text('Password') input[type='password']").first.fill(emp_pass)
    page.locator("div.oxd-input-group:has-text('Confirm Password') input[type='password']").fill(emp_pass)

    page.locator("button[type='submit']").click()
    page.wait_for_url("**/pim/viewPersonalDetails/**", timeout=25000)
    page.wait_for_load_state("networkidle")

    # Extract internal empNumber from URL
    emp_number = page.url.split("/")[-1]
    logger.info("Employee created successfully. Internal empNumber: %s", emp_number)

    # 3. Assign Admin as Direct Reporting Supervisor
    report_to_tab = page.locator("a:has-text('Report-to')")
    if report_to_tab.is_visible():
        report_to_tab.click()
    else:
        page.goto(
            f"{base_url}/web/index.php/pim/viewReportToDetails/empNumber/{emp_number}",
            wait_until="domcontentloaded",
        )
    page.wait_for_load_state("networkidle")

    page.locator(
        "div.orangehrm-horizontal-padding:has-text('Assigned Supervisors') button:has-text('Add')"
    ).click()
    page.wait_for_selector(".oxd-autocomplete-text-input input", timeout=10000)

    sup_input = page.locator(".oxd-autocomplete-text-input input")
    sup_input.fill(admin_first_token)
    page.wait_for_selector(".oxd-autocomplete-dropdown span", timeout=10000)
    page.locator(".oxd-autocomplete-dropdown span").first.click()

    # Select Reporting Method: Direct (exact text match)
    page.locator(".oxd-select-text").click()
    page.wait_for_selector(".oxd-select-dropdown", timeout=10000)
    page.locator(".oxd-select-dropdown").get_by_text("Direct", exact=True).click()

    page.locator("button[type='submit']:has-text('Save')").click()
    page.wait_for_selector(".oxd-toast", timeout=15000)
    page.wait_for_load_state("networkidle")
    logger.info("Supervisor '%s' assigned directly to employee '%s'", admin_name, first_name)

    # 4. Save credentials to test_context
    test_context["employee_user"] = emp_user
    test_context["employee_pass"] = emp_pass
    test_context["emp_number"] = emp_number
    test_context["first_name"] = first_name
    test_context["last_name"] = last_name

    DataRecorder.record(
        module="Time & Attendance",
        action="Employee Registration & Supervisor Assignment",
        fields={
            "Employee Name": f"{first_name} {last_name}",
            "Employee Id": emp_id,
            "Username": emp_user,
            "Supervisor": admin_name,
            "Reporting Method": "Direct",
        },
    )

    # 5. Logout Admin so Employee can log in
    _do_logout(page)


@when("the employee logs in and navigates to My Timesheets")
def employee_login_and_navigate_timesheets(page: Page, test_context: dict):
    logger.info("[STEP] When the employee logs in and navigates to My Timesheets")
    timesheet_page = TimesheetPage(page)

    _do_login(page, test_context["employee_user"], test_context["employee_pass"])
    timesheet_page.go_to_my_timesheets()

    DataRecorder.record(
        module="Time & Attendance",
        action="Employee Login & Navigate Timesheet",
        fields={"Username": test_context["employee_user"]},
    )


@when(parsers.parse('the employee enters project "{project}" and logs {hours:d} hours from Monday to Friday'))
def employee_enters_project_hours(page: Page, project: str, hours: int):
    logger.info(
        "[STEP] And the employee enters project '%s' and logs %d hours from Monday to Friday",
        project,
        hours,
    )
    timesheet_page = TimesheetPage(page)
    timesheet_page.start_editing_timesheet()
    timesheet_page.fill_weekly_hours(project_keyword=project, hours=f"{hours}.00")

    DataRecorder.record(
        module="Time & Attendance",
        action="Log Weekly Project Hours",
        fields={
            "Project": project,
            "Daily Hours": f"{hours}.00",
            "Days Logged": "Monday to Friday (40.00 hrs total)",
        },
    )


@when("saves and submits the timesheet")
def save_and_submit_timesheet(page: Page):
    logger.info("[STEP] And saves and submits the timesheet")
    timesheet_page = TimesheetPage(page)
    timesheet_page.save_timesheet()
    timesheet_page.submit_timesheet()

    DataRecorder.record(
        module="Time & Attendance",
        action="Timesheet Submission",
        fields={"Action": "Saved draft and submitted timesheet for supervisor approval"},
    )


@then(parsers.parse('the timesheet status should display "{expected_status}"'))
def verify_timesheet_status(page: Page, expected_status: str):
    logger.info("[STEP] Then the timesheet status should display '%s'", expected_status)
    timesheet_page = TimesheetPage(page)
    actual_status = timesheet_page.wait_for_status(expected_status)
    assert expected_status.lower() in actual_status.lower(), (
        f"Expected timesheet status '{expected_status}', but found '{actual_status}'"
    )
    logger.info("Timesheet status successfully verified as '%s'", actual_status)


@when("the supervisor logs in and reviews the employee timesheet")
def supervisor_reviews_employee_timesheet(page: Page, test_context: dict):
    logger.info("[STEP] When the supervisor logs in and reviews the employee timesheet")
    timesheet_page = TimesheetPage(page)

    _do_logout(page)
    _do_login(page, ConfigReader.get_username(), ConfigReader.get_password())
    timesheet_page.open_employee_timesheet(test_context["emp_number"])

    DataRecorder.record(
        module="Time & Attendance",
        action="Supervisor Review Timesheet",
        fields={"Employee Reviewed": test_context["first_name"]},
    )


@when(parsers.parse('rejects the timesheet with comment "{comment}"'))
def supervisor_rejects_timesheet(page: Page, comment: str):
    logger.info("[STEP] And rejects the timesheet with comment '%s'", comment)
    timesheet_page = TimesheetPage(page)
    timesheet_page.reject_timesheet(comment)

    DataRecorder.record(
        module="Time & Attendance",
        action="Supervisor Rejection",
        fields={"Decision": "Rejected", "Comment": comment},
    )


@when("the employee logs in and views their timesheet")
def employee_logs_in_views_timesheet(page: Page, test_context: dict):
    logger.info("[STEP] When the employee logs in and views their timesheet")
    timesheet_page = TimesheetPage(page)

    _do_logout(page)
    _do_login(page, test_context["employee_user"], test_context["employee_pass"])
    timesheet_page.go_to_my_timesheets()


@when(parsers.parse('the employee updates Wednesday hours to {hours} and re-submits the timesheet'))
def employee_updates_wednesday_hours(page: Page, hours: str):
    logger.info("[STEP] When the employee updates Wednesday hours to %s and re-submits the timesheet", hours)
    timesheet_page = TimesheetPage(page)
    timesheet_page.start_editing_timesheet()
    # Day index 2 corresponds to Wednesday
    timesheet_page.update_day_hours(day_index=2, new_hours=hours)
    timesheet_page.save_timesheet()
    timesheet_page.submit_timesheet()

    DataRecorder.record(
        module="Time & Attendance",
        action="Revise and Re-submit Timesheet",
        fields={"Wednesday Revised Hours": hours, "Status": "Re-submitted"},
    )


@when("the supervisor reviews the employee timesheet and clicks approve")
def supervisor_approves_timesheet(page: Page, test_context: dict):
    logger.info("[STEP] When the supervisor reviews the employee timesheet and clicks approve")
    timesheet_page = TimesheetPage(page)

    _do_logout(page)
    _do_login(page, ConfigReader.get_username(), ConfigReader.get_password())
    timesheet_page.open_employee_timesheet(test_context["emp_number"])
    timesheet_page.approve_timesheet()

    DataRecorder.record(
        module="Time & Attendance",
        action="Supervisor Timesheet Approval",
        fields={"Employee": test_context["first_name"], "Decision": "Approved"},
    )


@then("the timesheet should be locked from further employee edits")
def verify_timesheet_locked(page: Page, test_context: dict):
    logger.info("[STEP] And the timesheet should be locked from further employee edits")
    timesheet_page = TimesheetPage(page)

    _do_logout(page)
    _do_login(page, test_context["employee_user"], test_context["employee_pass"])
    timesheet_page.go_to_my_timesheets()
    timesheet_page.wait_for_status("Approved")

    assert timesheet_page.is_edit_locked(), (
        "Timesheet is NOT locked: Edit button is still accessible to employee after approval!"
    )
    logger.info("Validation confirmed: Timesheet is locked from further employee edits.")

    DataRecorder.record(
        module="Time & Attendance",
        action="Timesheet Lock Verification",
        fields={"Final Status": "Approved & Locked", "Employee Edit Disabled": True},
    )
