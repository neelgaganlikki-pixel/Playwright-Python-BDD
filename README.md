# OrangeHRM UI Automation Framework (Playwright + Python + Pytest-BDD)

A production-grade, enterprise-ready UI test automation framework built for the [OrangeHRM Open Source Demo](https://opensource-demo.orangehrmlive.com/) using **Python**, **Playwright**, and **pytest-bdd** (Cucumber-style BDD) following the **Page Object Model (POM)** architecture.

---

## 1. Architecture Overview

The framework follows a strict multi-layer separation of concerns:

```
+-------------------------------------------------------------+
|                     Gherkin Feature Files                   |
|         (Business-readable scenarios in features/*.feature)  |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                      Step Definitions                       |
|       (step_definitions/*.py - Maps Gherkin to actions)     |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                        Page Objects                         |
|     (pages/*.py - Encapsulates locators and user actions)    |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                      Playwright Engine                      |
|       (Native auto-waiting, browser contexts, sessions)     |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                   OrangeHRM Web Application                 |
+-------------------------------------------------------------+
```

### Key Architectural Principles
* **Zero `time.sleep()`**: 100% reliant on Playwright's native auto-waiting and dynamic locator assertions.
* **Strict Page Object Model**: Page locators and DOM interactions live exclusively inside `pages/`. Feature files and step definitions never contain raw CSS/XPath selectors.
* **Cucumber-style BDD**: Business-readable specifications in `.feature` files powered by `pytest-bdd`.
* **Zero Hardcoded Secrets**: Credentials, base URLs, and browser settings are dynamically loaded from environment variables and `.env`.
* **Comprehensive Reporting**: Rich self-contained HTML test reports (`reports/report.html`), automatic full-page failure screenshots (`screenshots/`), and detailed execution logs (`reports/test_execution.log`).

---

## 2. Technology Stack

* **Language**: Python 3.10+
* **Browser Automation**: [Playwright for Python](https://playwright.dev/python/)
* **Test Runner**: [pytest](https://docs.pytest.org/)
* **BDD Framework**: [pytest-bdd](https://pytest-bdd.readthedocs.io/)
* **Configuration Management**: [python-dotenv](https://github.com/theskumar/python-dotenv)
* **Reporting**: [pytest-html](https://pytest-html.readthedocs.io/) with embedded failure screenshots
* **Logging**: Standard Python `logging` with file and console formatters
* **CI/CD**: Jenkins Declarative Pipeline (`Jenkinsfile`)

---

## 3. Project Structure

```text
orangehrm-playwright-python/
│
├── features/                   # Gherkin BDD feature specifications
│   ├── login.feature           # Authentication & session tests
│   ├── employee.feature        # PIM employee management tests
│   ├── leave.feature           # Leave list & filter tests
│   ├── recruitment.feature     # Candidate recruitment tests
│   └── buzz.feature            # Buzz social newsfeed tests
│
├── pages/                      # Page Object Model classes
│   ├── __init__.py
│   ├── base_page.py            # Base page with common navigation & locators
│   ├── login_page.py           # Login page actions & validations
│   ├── dashboard_page.py       # Dashboard widgets & logout
│   ├── employee_page.py        # PIM Add & Search employee
│   ├── leave_page.py           # Leave filtering & table results
│   ├── recruitment_page.py     # Candidate management
│   └── buzz_page.py            # Status posting & feed verification
│
├── step_definitions/           # Step definition glue code
│   ├── __init__.py
│   ├── login_steps.py
│   ├── employee_steps.py
│   ├── leave_steps.py
│   ├── recruitment_steps.py
│   └── buzz_steps.py
│
├── tests/                      # Pytest test discovery entry point
│   └── test_features.py
│
├── config/                     # Configuration management
│   ├── __init__.py
│   └── config_reader.py        # Secure environment reader
│
├── utils/                      # Shared helper utilities
│   ├── __init__.py
│   ├── logger.py               # Centralized logging configuration
│   ├── test_data.py            # Dynamic collision-free test data generator
│   └── helpers.py              # Resilient Playwright helpers
│
├── reports/                    # Test execution reports and logs
│   ├── report.html             # Pytest HTML test report
│   └── test_execution.log      # Runtime log output
│
├── screenshots/                # Failure screenshots captured automatically
├── conftest.py                 # Pytest fixtures, hooks & Playwright setup
├── pytest.ini                  # Pytest configuration, CLI logging & markers
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment configuration
├── .env                        # Local environment configuration
├── .gitignore                  # Git ignore rules
├── Jenkinsfile                 # Jenkins CI/CD pipeline
└── README.md                   # Project documentation
```

---

## 4. Setup and Installation

### Prerequisites
* Python 3.10 or higher
* Git

### Step-by-step Setup

1. **Clone the repository or open the project folder**:
   ```bash
   cd "d:/Automation Testing/Playwright Python Bdd"
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**:
   ```bash
   python -m playwright install chromium
   ```

5. **Configure environment variables**:
   Copy `.env.example` to `.env` and adjust if needed:
   ```env
   BASE_URL=https://opensource-demo.orangehrmlive.com/
   ORANGEHRM_USERNAME=Admin
   ORANGEHRM_PASSWORD=admin123
   HEADLESS=true
   SLOW_MO=0
   BROWSER=chromium
   DEFAULT_TIMEOUT=30000
   ```

---

## 5. Test Execution

### Run all tests
```bash
pytest
```

### Run with Headed Browser (Visible UI)
Override via environment variable:
```bash
# Windows PowerShell
$env:HEADLESS="false"; pytest

# Bash / Linux / macOS
HEADLESS=false pytest
```

### Run with Slow Motion (Debug mode)
```bash
# Windows PowerShell
$env:SLOW_MO="500"; pytest

# Bash / Linux / macOS
SLOW_MO=500 pytest
```

### Run by Marker / Tag
```bash
# Run smoke tests only
pytest -m smoke

# Run regression tests only
pytest -m regression

# Run specific module
pytest -m login
pytest -m employee
pytest -m leave
pytest -m recruitment
pytest -m buzz
```

### Run a specific feature file
```bash
pytest tests/test_features.py -k "login"
pytest tests/test_features.py -k "employee"
```

---

## 6. Reporting and Artifacts

* **Pytest HTML Report**: Generated automatically at `reports/report.html`.
* **Execution Logs**: Detailed timestamped execution traces saved at `reports/test_execution.log`.
* **Automatic Failure Screenshots**: When any scenario step fails, a screenshot is automatically captured, stored in `screenshots/FAILED_<test_name>_<timestamp>.png`, and embedded directly into the HTML report.

---

## 7. CI/CD Integration (Jenkins)

The project includes an enterprise-ready `Jenkinsfile` supporting:
* Parameterized execution (`BROWSER`, `HEADLESS`, `SLOW_MO`, `TEST_MARKER`).
* Secure credential injection (`credentials('orangehrm-admin-password')`).
* Virtual environment creation and dependency installation.
* HTML report publication via Jenkins HTML Publisher Plugin.
* Screenshot and log archiving on completion.
