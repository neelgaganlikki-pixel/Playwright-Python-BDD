from pytest_bdd import when, then
from playwright.sync_api import Page
from pages.leave_page import LeavePage
from utils.logger import get_logger

logger = get_logger("LeaveSteps")


@when("the user navigates to the Leave module")
def navigate_to_leave(page: Page):
    leave_page = LeavePage(page)
    leave_page.navigate_to_leave()


@when("clicks the search button on the leave filter")
def click_search_leave(page: Page):
    leave_page = LeavePage(page)
    leave_page.click_search()


@when("clicks the reset button on the leave filter")
def click_reset_leave(page: Page):
    leave_page = LeavePage(page)
    leave_page.click_reset()


@then("the leave results section should be displayed")
def verify_leave_results_displayed(page: Page):
    leave_page = LeavePage(page)
    assert leave_page.is_leave_list_displayed(), "Leave results container was not displayed."
