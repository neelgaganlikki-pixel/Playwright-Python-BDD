import random
import string
from datetime import datetime


class TestDataGenerator:
    """
    Utility class for generating dynamic, collision-free test data.
    """

    @staticmethod
    def random_string(length: int = 5) -> str:
        return "".join(random.choices(string.ascii_letters, k=length))

    @staticmethod
    def random_digits(length: int = 4) -> str:
        return "".join(random.choices(string.digits, k=length))

    @classmethod
    def generate_employee_name(cls) -> tuple[str, str, str]:
        """
        Returns (first_name, middle_name, last_name)
        """
        suffix = cls.random_string(4)
        first_name = f"Auto{suffix}"
        middle_name = f"Mid{cls.random_string(3)}"
        last_name = f"QA{cls.random_string(4)}"
        return first_name, middle_name, last_name

    @classmethod
    def generate_employee_id(cls) -> str:
        return f"9{cls.random_digits(4)}"

    @classmethod
    def generate_candidate_data(cls) -> dict[str, str]:
        suffix = cls.random_string(4)
        return {
            "first_name": f"Cand{suffix}",
            "last_name": f"Tester{cls.random_string(3)}",
            "email": f"candidate_{suffix}_{cls.random_digits(3)}@testorangehrm.com",
            "contact_number": f"98765{cls.random_digits(5)}",
            "keywords": "QA, Playwright, Python, Automation",
            "notes": "Automated recruitment test candidate created by Playwright BDD suite.",
        }

    @classmethod
    def generate_buzz_post(cls) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        token = cls.random_string(6)
        return f"Automation Status Update [{token}] at {timestamp}"
