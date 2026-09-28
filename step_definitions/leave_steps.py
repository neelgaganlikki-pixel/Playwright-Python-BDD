from pytest_bdd import when, then
from playwright.sync_api import Page
from pages.leave_page import LeavePage
from utils.logger import get_logger
from utils.data_recorder import DataRecorder

logger = get_logger("LeaveSteps")


@when("the user navigates to the Leave module")
def navigate_to_leave(page: Page):
    logger.info("[STEP] When the user navigates to the Leave module")
    leave_page = LeavePage(page)
    leave_page.navigate_to_leave()
    logger.info("Successfully navigated to Leave module")


@when("clicks the search button on the leave filter")
def click_search_leave(page: Page):
    logger.info("[STEP] And clicks the search button on the leave filter")
    DataRecorder.record(
        module="Leave Management",
        action="Search Leave List",
        fields={"Action": "Applied search criteria on Leave List"},
    )
    leave_page = LeavePage(page)
    leave_page.click_search()
    logger.info("Search submitted on Leave List")


@when("clicks the reset button on the leave filter")
def click_reset_leave(page: Page):
    logger.info("[STEP] And clicks the reset button on the leave filter")
    DataRecorder.record(
        module="Leave Management",
        action="Reset Leave List Filters",
        fields={"Action": "Reset filters back to default"},
    )
    leave_page = LeavePage(page)
    leave_page.click_reset()
    logger.info("Reset filter submitted on Leave List")


@then("the leave results section should be displayed")
def verify_leave_results_displayed(page: Page):
    logger.info("[STEP] Then the leave results section should be displayed")
    leave_page = LeavePage(page)
    assert leave_page.is_leave_list_displayed(), "Leave results container was not displayed."
    records_info = leave_page.get_records_text()
    logger.info(f"Leave results container confirmed visible. Status: '{records_info}'")
