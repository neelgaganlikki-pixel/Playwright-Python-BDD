from pytest_bdd import when, then
from playwright.sync_api import Page
from pages.recruitment_page import RecruitmentPage
from utils.test_data import TestDataGenerator
from utils.logger import get_logger

logger = get_logger("RecruitmentSteps")


@when("the user navigates to the Recruitment module")
def navigate_to_recruitment(page: Page):
    rec_page = RecruitmentPage(page)
    rec_page.navigate_to_recruitment()


@then("the candidate records list should be visible")
def verify_candidate_records_visible(page: Page):
    rec_page = RecruitmentPage(page)
    rec_page.btn_add.wait_for(state="visible", timeout=20000)
    assert rec_page.btn_add.is_visible(), "Recruitment Add button / candidate list not visible."


@when("clicks on the Add Candidate button")
def click_add_candidate_button(page: Page):
    rec_page = RecruitmentPage(page)
    rec_page.click_add_candidate()


@when("enters candidate details")
def enter_candidate_details(page: Page, test_context: dict):
    cand_data = TestDataGenerator.generate_candidate_data()
    test_context["candidate_data"] = cand_data

    rec_page = RecruitmentPage(page)
    rec_page.fill_candidate_info(
        first_name=cand_data["first_name"],
        last_name=cand_data["last_name"],
        email=cand_data["email"],
        contact_number=cand_data["contact_number"],
    )


@when("saves the candidate")
def save_candidate_step(page: Page):
    rec_page = RecruitmentPage(page)
    rec_page.save_candidate()


@then("the candidate application details should be displayed")
def verify_candidate_application_details(page: Page):
    rec_page = RecruitmentPage(page)
    assert rec_page.is_candidate_saved(), "Candidate application details were not displayed after saving."
