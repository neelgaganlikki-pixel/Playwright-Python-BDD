================================================================================
ORANGEHRM UI TEST AUTOMATION FRAMEWORK
Technology Stack: Python 3 + Playwright + Pytest + Pytest-BDD (Cucumber Style)
Target Application: OrangeHRM Open Source Demo (https://opensource-demo.orangehrmlive.com/)
================================================================================

1. PROJECT OVERVIEW
--------------------------------------------------------------------------------
This project is an enterprise-grade UI test automation framework developed to 
automate business critical workflows of the OrangeHRM web application.

The framework adheres to the Page Object Model (POM) architectural design 
pattern and Cucumber-style Behavior-Driven Development (BDD) using Gherkin 
feature files and pytest-bdd.


2. TECHNOLOGY STACK & CORE LIBRARIES
--------------------------------------------------------------------------------
- Language:                Python 3.10+
- Browser Automation:      Playwright for Python (Synchronous API)
- Test Runner:             pytest (v9.x)
- BDD Framework:           pytest-bdd (v8.x) - Gherkin feature runner
- Design Pattern:          Page Object Model (POM)
- Reporting:               pytest-html (v4.x) with Base64 embedded screenshots
- Environment Config:      python-dotenv (.env configuration)
- Logging:                 Standard Python logging (Console + File)
- CI/CD:                   Jenkins Declarative Pipeline (Jenkinsfile)
- Version Control:         Git


3. ARCHITECTURAL DESIGN & DATA FLOW
--------------------------------------------------------------------------------
The framework enforces a strict separation of concerns across multiple layers:

    [ Gherkin .feature Files ]
                 |
                 v
    [ Step Definitions (pytest-bdd) ]
                 |
                 v
    [ Page Object Classes (pages/) ]
                 |
                 v
    [ Playwright API Engine ]
                 |
                 v
    [ OrangeHRM Web UI ]

Key Architectural Rules:
- ZERO time.sleep(): All synchronization relies exclusively on Playwright's 
  smart auto-waiting, locator.wait_for(), and page.wait_for_load_state().
- Strict Locator Encapsulation: All selectors live in page objects. No raw CSS 
  or XPath selectors are placed inside feature files or step definitions.
- Test Isolation: Every test scenario runs within an isolated BrowserContext 
  and Page instance to prevent session or cookie bleeding across tests.
- Dynamic Test Data: test_data.py generates collision-free, randomized data 
  (employee names, IDs, candidate emails, buzz status strings) on every run.
- Zero Hardcoded Secrets: Passwords and sensitive parameters are managed via 
  environment variables and .env files loaded through config_reader.py.


4. PROJECT DIRECTORY STRUCTURE
--------------------------------------------------------------------------------
orangehrm-playwright-python/
│
├── features/                   Gherkin BDD business scenarios
│   ├── login.feature           Authentication, validation, and session tests
│   ├── employee.feature        PIM employee creation and ID search tests
│   ├── leave.feature           Leave list filtering and reset tests
│   ├── recruitment.feature     Candidate list verification and applicant creation
│   └── buzz.feature            Social newsfeed posting and feed verification
│
├── pages/                      Page Object Model (POM) classes
│   ├── __init__.py             Exports all page classes
│   ├── base_page.py            Base class with shared navigation, header, & toasts
│   ├── login_page.py           Login interactions and error validation
│   ├── dashboard_page.py       Dashboard verification and user logout
│   ├── employee_page.py        PIM employee management actions
│   ├── leave_page.py           Leave module filters and results container
│   ├── recruitment_page.py     Recruitment candidate form and table actions
│   └── buzz_page.py            Buzz feed posting and post verification
│
├── step_definitions/           Pytest-BDD step definition glue code
│   ├── __init__.py
│   ├── login_steps.py          Steps for authentication and logout
│   ├── employee_steps.py       Steps for PIM workflows
│   ├── leave_steps.py          Steps for Leave workflows
│   ├── recruitment_steps.py    Steps for Recruitment workflows
│   └── buzz_steps.py           Steps for Buzz workflows
│
├── tests/                      Test execution and discovery
│   └── test_features.py        Binds Gherkin feature files to pytest via scenarios()
│
├── config/                     Configuration handling
│   ├── __init__.py
│   └── config_reader.py        Reads environment variables and .env settings
│
├── utils/                      Utility and helper functions
│   ├── __init__.py
│   ├── logger.py               Configures console and file logger (reports/test_execution.log)
│   ├── test_data.py            Collision-free test data generator
│   └── helpers.py              Resilient Playwright interaction helpers
│
├── reports/                    Generated execution reports and logs
│   ├── report.html             Pytest HTML test report
│   └── test_execution.log      Runtime execution log file
│
├── screenshots/                Automatically captured full-page failure screenshots
│
├── conftest.py                 Pytest fixtures (browser, context, page) and failure hooks
├── pytest.ini                  Pytest settings, markers, CLI logging configuration
├── requirements.txt            Python dependencies
├── .env.example                Template environment configuration file
├── .env                        Local environment file (contains default credentials)
├── .gitignore                  Git ignore rules for secrets and build artifacts
├── Jenkinsfile                 Enterprise CI/CD declarative pipeline
└── README.md                   Markdown documentation


5. IMPLEMENTED TEST SCENARIOS (12 TOTAL)
--------------------------------------------------------------------------------
Module: Authentication (features/login.feature)
  - test_successful_login_with_valid_credentials       [@smoke, @login]
  - test_unsuccessful_login_with_invalid_credentials     [@regression, @login]
  - test_login_validation_with_empty_credentials         [@regression, @login]
  - test_user_logs_out_successfully                    [@smoke, @login]

Module: PIM / Employee Management (features/employee.feature)
  - test_add_a_new_employee_successfully               [@smoke, @employee]
  - test_search_for_an_existing_employee_by_id         [@regression, @employee]

Module: Leave Management (features/leave.feature)
  - test_view_leave_list_and_apply_search_filter       [@smoke, @leave]
  - test_reset_leave_search_filter                     [@regression, @leave]

Module: Recruitment Management (features/recruitment.feature)
  - test_view_candidate_list_in_recruitment_module     [@smoke, @recruitment]
  - test_add_a_new_candidate_successfully             [@smoke, @recruitment]

Module: Buzz Social Feed (features/buzz.feature)
  - test_post_a_status_update_to_buzz_newsfeed         [@smoke, @buzz]
  - test_verify_buzz_feed_loads_existing_posts         [@regression, @buzz]


6. FIXTURES & HOOKS (conftest.py)
--------------------------------------------------------------------------------
- pytest_plugins:
    Globally registers all step definition modules so steps can be shared across
    any scenario.
- playwright_instance (scope: session):
    Manages the Playwright lifecycle using sync_playwright().
- browser (scope: session):
    Launches Chromium, Firefox, or WebKit based on config (supports headless,
    headed, and slow-mo execution).
- context (scope: function):
    Creates a dedicated BrowserContext with standard viewport (1280x720) for 
    each scenario to ensure total test isolation.
- page (scope: function):
    Instantiates a fresh page per scenario, sets navigation timeouts, tracks the
    active page reference for hooks, and closes upon test completion.
- pytest_runtest_makereport hook:
    Intercepts test failure, captures a full-page PNG to screenshots/, and
    embeds the image as Base64 into the pytest-html report.


7. EXECUTION COMMANDS
--------------------------------------------------------------------------------
Run all tests (Default Headless):
    pytest

Run in Headed mode (Visible Browser):
    PowerShell:    $env:HEADLESS="false"; pytest
    CMD:           set HEADLESS=false && pytest

Run with Slow Motion (e.g. 500ms delay to visually observe actions):
    PowerShell:    $env:HEADLESS="false"; $env:SLOW_MO="500"; pytest
    CMD:           set HEADLESS=false && set SLOW_MO=500 && pytest

Run by Tags / Markers:
    pytest -m smoke
    pytest -m regression
    pytest -m login
    pytest -m employee
    pytest -m leave
    pytest -m recruitment
    pytest -m buzz

List all tests without running:
    pytest --collect-only -q

Open HTML execution report:
    PowerShell:    Start-Process reports\report.html


8. CI/CD INTEGRATION (Jenkinsfile)
--------------------------------------------------------------------------------
The project includes a declarative Jenkins pipeline supporting:
- Parameterized execution (BROWSER, HEADLESS, SLOW_MO, TEST_MARKER).
- Secure credential binding for ORANGEHRM_PASSWORD.
- Automated virtualenv setup and Playwright browser installation.
- Automated publication of HTML test reports and screenshot archiving.
================================================================================
