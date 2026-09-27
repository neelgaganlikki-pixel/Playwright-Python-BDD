from pytest_bdd import when, then
from playwright.sync_api import Page
from pages.buzz_page import BuzzPage
from utils.test_data import TestDataGenerator
from utils.logger import get_logger

logger = get_logger("BuzzSteps")


@when("the user navigates to the Buzz module")
def navigate_to_buzz(page: Page):
    buzz_page = BuzzPage(page)
    buzz_page.go_to_buzz()


@when("writes a new status update")
def write_buzz_post(page: Page, test_context: dict):
    post_text = TestDataGenerator.generate_buzz_post()
    test_context["buzz_post_text"] = post_text
    buzz_page = BuzzPage(page)
    buzz_page.post_input.fill(post_text)


@when("clicks the post button")
def click_post_button(page: Page):
    buzz_page = BuzzPage(page)
    buzz_page.btn_post.click()
    page.wait_for_selector(".oxd-toast, .orangehrm-buzz-newsfeed", timeout=15000)


@then("the status update should appear in the Buzz newsfeed")
def verify_post_in_feed(page: Page, test_context: dict):
    post_text = test_context["buzz_post_text"]
    buzz_page = BuzzPage(page)
    assert buzz_page.is_post_in_feed(post_text), f"Buzz post '{post_text}' was not found in the newsfeed."


@then("the Buzz newsfeed container should be displayed")
def verify_buzz_newsfeed_displayed(page: Page):
    buzz_page = BuzzPage(page)
    buzz_page.newsfeed_container.wait_for(state="visible", timeout=20000)
    assert buzz_page.newsfeed_container.is_visible(), "Buzz newsfeed container was not displayed."
