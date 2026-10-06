from pathlib import Path
from pytest_bdd import scenarios

# Define path to features directory
FEATURES_DIR = Path(__file__).resolve().parent.parent / "features"

# Bind Gherkin feature files to pytest test runner
scenarios(str(FEATURES_DIR / "login.feature"))
scenarios(str(FEATURES_DIR / "employee.feature"))
scenarios(str(FEATURES_DIR / "leave.feature"))
scenarios(str(FEATURES_DIR / "recruitment.feature"))
scenarios(str(FEATURES_DIR / "buzz.feature"))
scenarios(str(FEATURES_DIR / "timesheet.feature"))

