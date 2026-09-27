from pytest_bdd import given, when, then, parsers
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from config.config_reader import ConfigReader
from utils.logger import get_logger

logger = get_logger("LoginSteps")


@given("the user navigates to the OrangeHRM login page")
def navigate_to_login(page: Page):
    login_page = LoginPage(page)
    login_page.load()
    expect(login_page.username_input).to_be_visible()


@given("the user is logged into the OrangeHRM portal")
def ensure_user_logged_in(page: Page):
    login_page = LoginPage(page)
    dashboard_page = DashboardPage(page)
    login_page.login()
    assert dashboard_page.is_dashboard_displayed(), "User was not redirected to Dashboard after login."


@when("the user submits valid credentials")
def submit_valid_credentials(page: Page):
    login_page = LoginPage(page)
    login_page.enter_username(ConfigReader.get_username())
    login_page.enter_password(ConfigReader.get_password())
    login_page.click_login()


@when(parsers.parse('the user enters username "{username}" and password "{password}"'))
def enter_custom_credentials(page: Page, username: str, password: str):
    login_page = LoginPage(page)
    login_page.enter_username(username)
    login_page.enter_password(password)


@when("clicks the login button")
def click_login(page: Page):
    login_page = LoginPage(page)
    login_page.click_login()


@when("the user submits empty credentials")
def submit_empty_credentials(page: Page):
    login_page = LoginPage(page)
    login_page.enter_username("")
    login_page.enter_password("")
    login_page.click_login()


@then("the user should be redirected to the Dashboard page")
def verify_dashboard_redirection(page: Page):
    dashboard_page = DashboardPage(page)
    assert dashboard_page.is_dashboard_displayed(), "Dashboard was not displayed."


@then("the dashboard header should be displayed")
def verify_dashboard_header(page: Page):
    dashboard_page = DashboardPage(page)
    header = dashboard_page.get_dashboard_header_text()
    assert "Dashboard" in header, f"Expected 'Dashboard' in header, got '{header}'"


@then(parsers.parse('an error message stating "{expected_error}" should be displayed'))
def verify_login_error_message(page: Page, expected_error: str):
    login_page = LoginPage(page)
    error_msg = login_page.get_error_message()
    assert expected_error.lower() in error_msg.lower(), (
        f"Expected error message '{expected_error}', but got '{error_msg}'"
    )


@then(parsers.parse('input field validation message "{expected_validation}" should be displayed'))
def verify_field_required_message(page: Page, expected_validation: str):
    login_page = LoginPage(page)
    user_req = login_page.get_username_required_message()
    pwd_req = login_page.get_password_required_message()
    assert expected_validation in user_req or expected_validation in pwd_req, (
        f"Validation '{expected_validation}' not displayed. Found: username='{user_req}', password='{pwd_req}'"
    )


@when("the user clicks the logout button")
def click_logout(page: Page):
    dashboard_page = DashboardPage(page)
    dashboard_page.logout()


@then("the user should be redirected to the login page")
def verify_login_page_redirection(page: Page):
    login_page = LoginPage(page)
    assert login_page.is_at_login_page(), "User was not redirected back to Login page."
