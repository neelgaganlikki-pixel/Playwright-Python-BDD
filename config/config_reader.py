import os
from pathlib import Path
from dotenv import load_dotenv

# Automatically locate the .env file in the project root
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)


class ConfigReader:
    """
    Centralized configuration manager reading from environment variables
    and .env files with sensible defaults.
    """

    @classmethod
    def get_base_url(cls) -> str:
        return os.getenv("BASE_URL", "https://opensource-demo.orangehrmlive.com/").strip()

    @classmethod
    def get_username(cls) -> str:
        return os.getenv("ORANGEHRM_USERNAME", "Admin").strip()

    @classmethod
    def get_password(cls) -> str:
        password = os.getenv("ORANGEHRM_PASSWORD", "")
        if not password:
            # Fallback to standard demo password if not set in environment
            password = os.getenv("DEFAULT_ORANGEHRM_PASSWORD", "admin123")
        return password

    @classmethod
    def is_headless(cls) -> bool:
        headless_val = os.getenv("HEADLESS", "true").strip().lower()
        return headless_val in ("true", "1", "yes", "y")

    @classmethod
    def get_slow_mo(cls) -> int:
        try:
            return int(os.getenv("SLOW_MO", "0").strip())
        except ValueError:
            return 0

    @classmethod
    def get_browser(cls) -> str:
        return os.getenv("BROWSER", "chromium").strip().lower()

    @classmethod
    def get_default_timeout(cls) -> int:
        try:
            return int(os.getenv("DEFAULT_TIMEOUT", "30000").strip())
        except ValueError:
            return 30000

    @classmethod
    def get_timeout(cls) -> int:
        return cls.get_default_timeout()

    # -------------------------------------------------------------------------
    # Jenkins CI/CD Configuration
    # -------------------------------------------------------------------------

    @classmethod
    def get_jenkins_url(cls) -> str:
        return os.getenv("JENKINS_URL", "http://localhost:8080").strip().rstrip("/")

    @classmethod
    def get_jenkins_user(cls) -> str:
        return os.getenv("JENKINS_USER", "").strip()

    @classmethod
    def get_jenkins_api_token(cls) -> str:
        return os.getenv("JENKINS_API_TOKEN", "").strip()

    @classmethod
    def get_jenkins_job_name(cls) -> str:
        return os.getenv("JENKINS_JOB_NAME", "OrangeHRM-Playwright-BDD").strip()

    # -------------------------------------------------------------------------
    # Self-Healing Automation Configuration
    # -------------------------------------------------------------------------

    @classmethod
    def is_self_healing_enabled(cls) -> bool:
        return os.getenv("SELF_HEALING_ENABLED", "true").strip().lower() in ("true", "1", "yes")

    @classmethod
    def get_self_healing_max_attempts(cls) -> int:
        try:
            return int(os.getenv("SELF_HEALING_MAX_ATTEMPTS", "3").strip())
        except ValueError:
            return 3

    @classmethod
    def should_save_healed_locators(cls) -> bool:
        return os.getenv("SELF_HEALING_SAVE_LOCATORS", "true").strip().lower() in ("true", "1", "yes")

    @classmethod
    def get_self_healing_fallback_timeout(cls) -> int:
        try:
            return int(os.getenv("SELF_HEALING_FALLBACK_TIMEOUT", "4000").strip())
        except ValueError:
            return 4000
