from pytest_bdd import when, then
from playwright.sync_api import Page
from pages.recruitment_page import RecruitmentPage
from utils.test_data import TestDataGenerator
from utils.logger import get_logger
from utils.data_recorder import DataRecorder

logger = get_logger("RecruitmentSteps")


@when("the user navigates to the Recruitment module")
def navigate_to_recruitment(page: Page):
    logger.info("[STEP] When the user navigates to the Recruitment module")
    rec_page = RecruitmentPage(page)
    rec_page.navigate_to_recruitment()
    logger.info("Successfully navigated to Recruitment module")


@then("the candidate records list should be visible")
def verify_candidate_records_visible(page: Page):
    logger.info("[STEP] Then the candidate records list should be visible")
    rec_page = RecruitmentPage(page)
    rec_page.btn_add.wait_for(state="visible", timeout=20000)
    assert rec_page.btn_add.is_visible(), "Recruitment Add button / candidate list not visible."
    logger.info("Candidate records list view and Add button confirmed visible")


@when("clicks on the Add Candidate button")
def click_add_candidate_button(page: Page):
    logger.info("[STEP] And clicks on the Add Candidate button")
    rec_page = RecruitmentPage(page)
    rec_page.click_add_candidate()
    logger.info("Add Candidate form is open")


@when("enters candidate details")
def enter_candidate_details(page: Page, test_context: dict):
    cand_data = TestDataGenerator.generate_candidate_data()
    test_context["candidate_data"] = cand_data

    logger.info(
        f"[STEP] And enters candidate details: "
        f"Name='{cand_data['first_name']} {cand_data['last_name']}', "
        f"Email='{cand_data['email']}', Contact='{cand_data['contact_number']}'"
    )

    DataRecorder.record(
        module="Recruitment",
        action="Add New Candidate",
        fields={
            "First Name": cand_data["first_name"],
            "Last Name": cand_data["last_name"],
            "Email": cand_data["email"],
            "Contact Number": cand_data["contact_number"],
            "Keywords": cand_data.get("keywords", "QA, Playwright, Automation"),
        },
    )

    rec_page = RecruitmentPage(page)
    rec_page.fill_candidate_info(
        first_name=cand_data["first_name"],
        last_name=cand_data["last_name"],
        email=cand_data["email"],
        contact_number=cand_data["contact_number"],
    )
    logger.info("Candidate fields populated")


@when("saves the candidate")
def save_candidate_step(page: Page):
    logger.info("[STEP] And saves the candidate")
    rec_page = RecruitmentPage(page)
    rec_page.save_candidate()
    logger.info("Candidate submitted, waiting for confirmation")


@then("the candidate application details should be displayed")
def verify_candidate_application_details(page: Page):
    logger.info("[STEP] Then the candidate application details should be displayed")
    rec_page = RecruitmentPage(page)
    assert rec_page.is_candidate_saved(), "Candidate application details were not displayed after saving."
    logger.info("Candidate application details successfully verified")
