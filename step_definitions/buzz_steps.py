from pytest_bdd import when, then
from playwright.sync_api import Page
from pages.buzz_page import BuzzPage
from utils.test_data import TestDataGenerator
from utils.logger import get_logger
from utils.data_recorder import DataRecorder

logger = get_logger("BuzzSteps")


@when("the user navigates to the Buzz module")
def navigate_to_buzz(page: Page):
    logger.info("[STEP] When the user navigates to the Buzz module")
    buzz_page = BuzzPage(page)
    buzz_page.go_to_buzz()
    logger.info("Successfully navigated to Buzz module")


@when("writes a new status update")
def write_buzz_post(page: Page, test_context: dict):
    post_text = TestDataGenerator.generate_buzz_post()
    test_context["buzz_post_text"] = post_text
    logger.info(f"[STEP] And writes a new status update: '{post_text}'")
    DataRecorder.record(
        module="Buzz Newsfeed",
        action="Publish Status Update",
        fields={"Status Post Content": post_text},
    )
    buzz_page = BuzzPage(page)
    buzz_page.post_input.fill(post_text)


@when("clicks the post button")
def click_post_button(page: Page):
    logger.info("[STEP] And clicks the post button")
    buzz_page = BuzzPage(page)
    buzz_page.btn_post.click()
    page.wait_for_selector(".oxd-toast, .orangehrm-buzz-newsfeed", timeout=15000)
    logger.info("Post button clicked and response acknowledged")


@then("the status update should appear in the Buzz newsfeed")
def verify_post_in_feed(page: Page, test_context: dict):
    post_text = test_context["buzz_post_text"]
    logger.info(f"[STEP] Then the status update should appear in the Buzz newsfeed: '{post_text}'")
    buzz_page = BuzzPage(page)
    assert buzz_page.is_post_in_feed(post_text), f"Buzz post '{post_text}' was not found in the newsfeed."
    logger.info("Buzz post confirmed visible in newsfeed")


@then("the Buzz newsfeed container should be displayed")
def verify_buzz_newsfeed_displayed(page: Page):
    logger.info("[STEP] Then the Buzz newsfeed container should be displayed")
    buzz_page = BuzzPage(page)
    buzz_page.newsfeed_container.wait_for(state="visible", timeout=20000)
    assert buzz_page.newsfeed_container.is_visible(), "Buzz newsfeed container was not displayed."
    logger.info("Buzz newsfeed container verified visible")
