from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage


class BuzzPage(BasePage):
    """
    Page Object representing the OrangeHRM Buzz Social Media Newsfeed.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        self.post_input = page.locator("textarea.oxd-buzz-post-input")
        self.btn_post = page.locator("button[type='submit']:has-text('Post')")
        self.newsfeed_container = page.locator(".orangehrm-buzz-newsfeed")
        self.post_cards = page.locator(".orangehrm-buzz-newsfeed-posts .oxd-sheet")
        self.post_texts = page.locator(".orangehrm-buzz-post-body-text")

    def go_to_buzz(self) -> None:
        self.logger.info("Opening Buzz module")
        self.navigate_to_buzz()
        self.post_input.wait_for(state="visible", timeout=20000)

    def create_post(self, content: str) -> None:
        self.logger.info(f"Publishing Buzz post: {content}")
        self.post_input.wait_for(state="visible", timeout=15000)
        self.post_input.fill("")
        self.post_input.fill(content)
        self.btn_post.click()
        # Wait for toast confirmation or page update
        self.page.wait_for_selector(".oxd-toast, .orangehrm-buzz-post-body-text", timeout=15000)
        self.page.wait_for_load_state("networkidle")

    def is_post_in_feed(self, content: str, timeout: int = 15000) -> bool:
        self.logger.info(f"Checking if post content '{content}' is present in feed")
        try:
            target_post = self.page.locator(f".orangehrm-buzz-post-body-text:has-text('{content}')")
            target_post.first.wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            # Fallback: check if content exists anywhere in newsfeed
            return content in self.newsfeed_container.inner_text()

    def get_latest_post_text(self) -> str:
        try:
            self.post_texts.first.wait_for(state="visible", timeout=10000)
            return self.post_texts.first.inner_text().strip()
        except PlaywrightTimeoutError:
            return ""
