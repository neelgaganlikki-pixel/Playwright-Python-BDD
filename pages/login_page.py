from playwright.sync_api import Page
from pages.base_page import BasePage
from config.config_reader import ConfigReader


class LoginPage(BasePage):
    """
    Page Object representing the OrangeHRM Login Page with integrated self-healing.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Standard Locators (preserved for backwards compatibility and direct inspection)
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
        self.heal_wait_for(
            element_name="Login Username Input",
            primary="input[name='username']",
            fallbacks=[
                "input[placeholder='Username']",
                "#txtUsername",
                "input[type='text']",
                "[data-testid='username']",
            ],
            timeout=30000,
        )

    def enter_username(self, username: str) -> None:
        self.logger.info(f"Entering username: {username}")
        self.heal_fill(
            element_name="Username Field",
            primary="input[name='username']",
            text=username,
            fallbacks=[
                "input[placeholder='Username']",
                "#txtUsername",
                "input[type='text']",
                "[data-testid='username']",
                "//input[@name='username']",
            ],
        )

    def enter_password(self, password: str) -> None:
        self.logger.info("Entering password")
        self.heal_fill(
            element_name="Password Field",
            primary="input[name='password']",
            text=password,
            fallbacks=[
                "input[placeholder='Password']",
                "#txtPassword",
                "input[type='password']",
                "[data-testid='password']",
                "//input[@name='password']",
            ],
        )

    def click_login(self) -> None:
        self.logger.info("Clicking Login button")
        self.heal_click(
            element_name="Login Submit Button",
            primary="button[type='submit']",
            fallbacks=[
                "button:has-text('Login')",
                "#btnLogin",
                ".orangehrm-login-button",
                "button.oxd-button--main",
                "//button[@type='submit']",
            ],
        )

    def login(self, username: str = None, password: str = None) -> None:
        user = username if username is not None else ConfigReader.get_username()
        pwd = password if password is not None else ConfigReader.get_password()
        self.load()
        self.enter_username(user)
        self.enter_password(pwd)
        self.click_login()

    def get_error_message(self) -> str:
        try:
            return self.heal_get_text(
                element_name="Login Error Alert",
                primary=".oxd-alert-content-text",
                fallbacks=[
                    ".oxd-alert-content",
                    "p.oxd-alert-content-text",
                    ".oxd-alert",
                ],
                timeout=8000,
            )
        except Exception:
            return ""

    def get_username_required_message(self) -> str:
        try:
            return self.heal_get_text(
                element_name="Username Required Message",
                primary="div.oxd-input-group:has(input[name='username']) .oxd-input-group__message",
                fallbacks=[
                    "div.oxd-input-group:has(input[name='username']) span.oxd-input-field-error-message",
                    ".oxd-input-group:first-child .oxd-input-group__message",
                ],
                timeout=5000,
            )
        except Exception:
            return ""

    def get_password_required_message(self) -> str:
        try:
            return self.heal_get_text(
                element_name="Password Required Message",
                primary="div.oxd-input-group:has(input[name='password']) .oxd-input-group__message",
                fallbacks=[
                    "div.oxd-input-group:has(input[name='password']) span.oxd-input-field-error-message",
                    ".oxd-input-group:nth-child(2) .oxd-input-group__message",
                ],
                timeout=5000,
            )
        except Exception:
            return ""

    def is_at_login_page(self) -> bool:
        try:
            self.page.wait_for_url("**/auth/login**", timeout=10000)
            self.heal_wait_for(
                element_name="Login Form Element",
                primary="input[name='username']",
                fallbacks=[
                    "button[type='submit']",
                    ".orangehrm-login-form",
                    "h5:has-text('Login')",
                    "input[placeholder='Username']",
                ],
                timeout=10000,
            )
            return True
        except Exception:
            return False

