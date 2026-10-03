import time
from playwright.sync_api import Page
from pages.base_page import BasePage


class BuzzPage(BasePage):
    """
    Page Object representing the OrangeHRM Buzz Social Media Newsfeed with self-healing.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Standard locators preserved for direct inspection
        self.post_input = page.locator("textarea.oxd-buzz-post-input")
        self.btn_post = page.locator("button[type='submit']")
        self.newsfeed_container = page.locator(".orangehrm-buzz-newsfeed")
        self.post_cards = page.locator(".orangehrm-buzz-newsfeed-posts .oxd-sheet")
        self.post_texts = page.locator(".orangehrm-buzz-post-body-text")

    def go_to_buzz(self) -> None:
        self.logger.info("Opening Buzz module")
        self.navigate_to_buzz()
        self.heal_wait_for(
            element_name="Buzz Post Textarea",
            primary="textarea.oxd-buzz-post-input",
            fallbacks=[
                "textarea[placeholder*='mind']",
                ".oxd-buzz-post-input",
                "form textarea",
            ],
            timeout=20000,
        )

    def create_post(self, content: str) -> None:
        self.logger.info(f"Publishing Buzz post: {content}")
        self.heal_fill(
            element_name="Buzz Status Post Input",
            primary="textarea.oxd-buzz-post-input",
            text=content,
            fallbacks=[
                "textarea[placeholder*='mind']",
                ".oxd-buzz-post-input",
                "//textarea[contains(@class, 'oxd-buzz-post-input')]",
            ],
            timeout=15000,
        )
        self.heal_click(
            element_name="Buzz Submit Post Button",
            primary="button[type='submit']",
            fallbacks=[
                "button:has-text('Post')",
                ".oxd-buzz-post-slot button",
                "//button[@type='submit']",
            ],
            timeout=10000,
        )
        try:
            self.page.wait_for_selector(".oxd-toast", timeout=5000)
        except Exception:
            pass

    def is_post_in_feed(self, content: str, max_attempts: int = 15) -> bool:
        """
        Polls for post presence in the Buzz newsfeed with periodic reload
        to account for distributed read-replica sync delays.
        """
        self.logger.info(f"Checking if post content '{content}' is present in feed")
        target_locator = self.page.locator(".orangehrm-buzz-post-body-text").filter(has_text=content)

        for attempt in range(1, max_attempts + 1):
            try:
                if target_locator.first.is_visible():
                    self.logger.info("Post '%s' found in feed on attempt %d", content, attempt)
                    return True
            except Exception:
                pass

            # Fast check against full newsfeed text content
            try:
                feed_text = self.newsfeed_container.inner_text()
                if content in feed_text:
                    self.logger.info("Post '%s' detected in newsfeed container text on attempt %d", content, attempt)
                    return True
            except Exception:
                pass

            # Reload periodically (every 4 attempts) to refresh cache/read-replica
            if attempt % 4 == 0 and attempt < max_attempts:
                self.logger.info("Refreshing Buzz page to pull updated feed (attempt %d/%d)...", attempt, max_attempts)
                try:
                    self.page.reload(wait_until="domcontentloaded")
                    self.page.wait_for_timeout(2000)
                except Exception:
                    pass
            else:
                self.page.wait_for_timeout(1000)

        return False

    def get_latest_post_text(self) -> str:
        try:
            return self.heal_get_text(
                element_name="Latest Buzz Post Text",
                primary=".orangehrm-buzz-post-body-text",
                fallbacks=[
                    ".oxd-sheet .orangehrm-buzz-post-body-text",
                    ".orangehrm-buzz-newsfeed-posts p",
                ],
                timeout=10000,
            )
        except Exception:
            return ""

