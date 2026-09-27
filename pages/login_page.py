from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage
from config.config_reader import ConfigReader


class LoginPage(BasePage):
    """
    Page Object representing the OrangeHRM Login Page.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Login specific locators
        self.username_input = page.locator("input[name='username']")
        self.password_input = page.locator("input[name='password']")
        self.submit_button = page.locator("button[type='submit']")
        self.error_alert = page.locator(".oxd-alert-content-text")
        self.username_required_msg = page.locator(
            "div.oxd-input-group:has(input[name='username']) .oxd-input-group__message"
        )
        self.password_required_msg = page.locator(
            "div.oxd-input-group:has(input[name='password']) .oxd-input-group__message"
        )
        self.forgot_password_link = page.locator(".orangehrm-login-forgot")

    def load(self, url: str = None) -> None:
        target_url = url or ConfigReader.get_base_url()
        self.navigate(target_url)
        self.username_input.wait_for(state="visible", timeout=30000)

    def enter_username(self, username: str) -> None:
        self.logger.info(f"Entering username: {username}")
        self.username_input.fill("")
        self.username_input.fill(username)

    def enter_password(self, password: str) -> None:
        self.logger.info("Entering password")
        self.password_input.fill("")
        self.password_input.fill(password)

    def click_login(self) -> None:
        self.logger.info("Clicking Login button")
        self.submit_button.click()

    def login(self, username: str = None, password: str = None) -> None:
        user = username if username is not None else ConfigReader.get_username()
        pwd = password if password is not None else ConfigReader.get_password()
        self.load()
        self.enter_username(user)
        self.enter_password(pwd)
        self.click_login()

    def get_error_message(self) -> str:
        try:
            self.error_alert.wait_for(state="visible", timeout=10000)
            return self.error_alert.inner_text().strip()
        except PlaywrightTimeoutError:
            return ""

    def get_username_required_message(self) -> str:
        try:
            self.username_required_msg.wait_for(state="visible", timeout=5000)
            return self.username_required_msg.inner_text().strip()
        except PlaywrightTimeoutError:
            return ""

    def get_password_required_message(self) -> str:
        try:
            self.password_required_msg.wait_for(state="visible", timeout=5000)
            return self.password_required_msg.inner_text().strip()
        except PlaywrightTimeoutError:
            return ""

    def is_at_login_page(self) -> bool:
        try:
            self.username_input.wait_for(state="visible", timeout=10000)
            return True
        except PlaywrightTimeoutError:
            return False
