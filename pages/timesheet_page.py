from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage
from config.config_reader import ConfigReader
from utils.logger import get_logger

logger = get_logger("TimesheetPage")


class TimesheetPage(BasePage):
    """
    Page Object representing the OrangeHRM Time & Attendance module.
    Encapsulates My Timesheets, Employee Timesheets, and Approval workflows
    with built-in self-healing and robust locator fallbacks.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Navigation & Topbar
        self.time_module_menu = page.locator("a[href*='viewTimeModule']")
        self.my_timesheet_menu = page.locator("a[href*='viewMyTimesheet']")
        self.employee_timesheet_menu = page.locator("a[href*='viewEmployeeTimesheet']")

        # Action Buttons
        self.btn_create_timesheet = page.locator("button:has-text('Create Timesheet')")
        self.btn_edit = page.locator("button:has-text('Edit')")
        self.btn_cancel = page.locator("button:has-text('Cancel')")
        self.btn_reset = page.locator("button:has-text('Reset')")
        self.btn_save = page.locator("button:has-text('Save')")
        self.btn_submit = page.locator("button:has-text('Submit')")
        self.btn_reject = page.locator("button:has-text('Reject')")
        self.btn_approve = page.locator("button:has-text('Approve')")

        # Status & Header
        self.status_label = page.locator(".oxd-text--subtitle-2").filter(has_text="Status:")

        # Table & Form inputs
        self.timesheet_table = page.locator(".orangehrm-timesheet-table")
        self.table_rows = page.locator(".orangehrm-timesheet-table tbody tr")

        # Comment Textarea
        self.comment_textarea = page.locator("textarea")

        # Rejection Modal Dialog (if present)
        self.modal_comment_textarea = page.locator(
            ".orangehrm-modal-container textarea, .oxd-dialog-container-default textarea, div[role='dialog'] textarea"
        )
        self.modal_btn_reject = page.locator(
            ".orangehrm-modal-container button:has-text('Reject'), .oxd-dialog-container-default button:has-text('Reject'), div[role='dialog'] button:has-text('Reject')"
        )

    def ensure_time_module_enabled(self) -> None:
        """
        Self-healing guard: Checks if Time module is enabled in Module Configuration.
        If disabled (e.g. by other users on shared demo instance), automatically re-enables it.
        """
        try:
            if not self.time_module_menu.is_visible():
                self.logger.warning("Time module not visible in sidebar. Checking Module Configuration...")
                base = ConfigReader.get_base_url().rstrip("/")
                self.page.goto(f"{base}/web/index.php/admin/viewModules", wait_until="domcontentloaded")
                self.page.wait_for_load_state("networkidle")
                switches = self.page.locator(".oxd-switch-input").all()
                if len(switches) > 3:
                    switches[3].click()
                    self.page.locator("button[type='submit']:has-text('Save')").click()
                    self.page.wait_for_selector(".oxd-toast", timeout=15000)
                    self.page.wait_for_load_state("networkidle")
                    self.logger.info("Self-healed: Time Module successfully re-enabled!")
        except Exception as e:
            self.logger.debug("ensure_time_module_enabled exception (ignored): %s", e)

    def go_to_my_timesheets(self) -> None:
        """Navigates directly to the current user's Timesheet."""
        self.logger.info("Navigating to My Timesheets page")
        base = ConfigReader.get_base_url().rstrip("/")
        self.page.goto(
            f"{base}/web/index.php/time/viewMyTimesheet",
            wait_until="domcontentloaded",
        )
        self.page.wait_for_load_state("networkidle")
        self.status_label.first.wait_for(state="visible", timeout=20000)

    def go_to_employee_timesheets(self) -> None:
        """Navigates to the Supervisor/Admin Employee Timesheets management page."""
        self.logger.info("Navigating to Employee Timesheets management page")
        base = ConfigReader.get_base_url().rstrip("/")
        self.page.goto(
            f"{base}/web/index.php/time/viewEmployeeTimesheet",
            wait_until="domcontentloaded",
        )
        self.page.wait_for_load_state("networkidle")

    def open_employee_timesheet(self, emp_number: str) -> None:
        """
        Navigates directly to a specific employee's Timesheet by empNumber
        for supervisor review and approval actions.
        """
        self.logger.info("Navigating to timesheet for employee number %s", emp_number)
        base = ConfigReader.get_base_url().rstrip("/")
        self.page.goto(
            f"{base}/web/index.php/time/viewTimesheet/employeeId/{emp_number}",
            wait_until="domcontentloaded",
        )
        self.page.wait_for_load_state("networkidle")
        self.status_label.first.wait_for(state="visible", timeout=20000)

    def get_status(self) -> str:
        """Extracts the current timesheet status string (e.g. 'Submitted', 'Approved', 'Rejected')."""
        self.status_label.first.wait_for(state="visible", timeout=15000)
        raw_text = self.status_label.first.inner_text().strip()
        status = raw_text.replace("Status:", "").strip()
        self.logger.info("Current timesheet status retrieved: '%s'", status)
        return status

    def wait_for_status(self, expected_status: str, timeout: int = 20000) -> str:
        """
        Waits for the timesheet status subtitle to contain expected_status.
        Handles reactive SPA DOM text updates seamlessly.
        """
        self.logger.info("Waiting for timesheet status to contain: '%s'", expected_status)
        target = self.status_label.filter(has_text=expected_status).first
        target.wait_for(state="visible", timeout=timeout)
        raw_text = target.inner_text().strip()
        status = raw_text.replace("Status:", "").strip()
        self.logger.info("Timesheet status confirmed: '%s'", status)
        return status

    def start_editing_timesheet(self) -> None:
        """Clicks Create Timesheet or Edit button to enter edit mode."""
        if self.btn_create_timesheet.is_visible():
            self.logger.info("Timesheet not initialized; clicking Create Timesheet")
            self.btn_create_timesheet.click()
            self.page.wait_for_load_state("networkidle")

        if self.btn_edit.is_visible():
            self.logger.info("Clicking Edit button on timesheet")
            self.btn_edit.click()
            self.page.wait_for_load_state("networkidle")

        self.btn_save.wait_for(state="visible", timeout=15000)

    def fill_weekly_hours(self, project_keyword: str = "Apache", hours: str = "8.00") -> None:
        """
        Fills the Project autocomplete, selects an activity, and sets daily hours
        for Monday through Friday (indices 0 to 4 in oxd-input fields).
        """
        self.logger.info("Filling weekly timesheet hours for project: %s", project_keyword)
        row = self.table_rows.first
        row.wait_for(state="visible", timeout=15000)

        # Select project via autocomplete
        proj_input = row.locator(".oxd-autocomplete-text-input input")
        proj_input.fill("")
        proj_input.fill(project_keyword)
        self.page.wait_for_selector(".oxd-autocomplete-dropdown span", timeout=10000)
        self.page.locator(".oxd-autocomplete-dropdown span").first.click()

        # Select first activity
        activity_dropdown = row.locator(".oxd-select-text")
        activity_dropdown.click()
        self.page.wait_for_selector(".oxd-select-dropdown span", timeout=10000)
        self.page.locator(".oxd-select-dropdown span").first.click()

        # Fill Mon - Fri hours (first 5 oxd-input elements in row)
        day_inputs = row.locator("input.oxd-input").all()
        for idx in range(min(5, len(day_inputs))):
            day_inputs[idx].fill("")
            day_inputs[idx].fill(hours)

        self.logger.info("Filled %s hours/day for Monday through Friday", hours)

    def update_day_hours(self, day_index: int, new_hours: str) -> None:
        """Updates hours for a specific day index (0=Mon, 1=Tue, 2=Wed, etc.)."""
        self.logger.info("Updating day index %d hours to '%s'", day_index, new_hours)
        row = self.table_rows.first
        row.wait_for(state="visible", timeout=15000)
        target_input = row.locator("input.oxd-input").nth(day_index)
        target_input.fill("")
        target_input.fill(new_hours)

    def save_timesheet(self) -> None:
        """Clicks Save and waits for confirmation."""
        self.logger.info("Saving timesheet draft")
        self.btn_save.click()
        self.page.wait_for_selector(".oxd-toast", timeout=15000)
        self.page.wait_for_load_state("networkidle")

    def submit_timesheet(self) -> None:
        """Submits the timesheet for supervisor approval."""
        self.logger.info("Submitting timesheet for approval")
        self.btn_submit.wait_for(state="visible", timeout=15000)
        self.btn_submit.click()
        self.page.wait_for_selector(".oxd-toast", timeout=15000)
        self.page.wait_for_load_state("networkidle")

    def search_and_view_employee_timesheet(self, employee_first_name: str, emp_number: str = None) -> None:
        """
        Searches for an employee timesheet by name or navigates directly via emp_number.
        """
        if emp_number:
            self.open_employee_timesheet(emp_number)
            return

        self.logger.info("Searching employee timesheet for: %s", employee_first_name)
        self.go_to_employee_timesheets()
        emp_input = self.page.locator(".oxd-autocomplete-text-input input")
        emp_input.fill("")
        emp_input.fill(employee_first_name)
        self.page.wait_for_selector(".oxd-autocomplete-dropdown span", timeout=10000)
        match_opt = self.page.locator(".oxd-autocomplete-dropdown span").filter(has_text=employee_first_name)
        if match_opt.count() > 0:
            match_opt.first.click()
        else:
            self.page.locator(".oxd-autocomplete-dropdown span").first.click()

        view_submit = self.page.locator("button[type='submit']:has-text('View')")
        view_submit.click()
        self.page.wait_for_load_state("networkidle")

        # If a table of timesheets is rendered, click the first row's view action
        if self.page.locator(".oxd-table-card").count() > 0:
            first_view = self.page.locator(".oxd-table-card").first.locator("button:has-text('View')")
            first_view.click()
            self.page.wait_for_load_state("networkidle")

        self.status_label.first.wait_for(state="visible", timeout=15000)

    def reject_timesheet(self, comment: str) -> None:
        """
        Supervisor rejects timesheet with comment.
        Handles both inline comment textarea and dialog-based textarea modal.
        """
        self.logger.info("Rejecting employee timesheet with comment: %s", comment)

        # 1. Fill comment if textarea is visible on page beforehand
        if self.comment_textarea.is_visible():
            self.logger.info("Filling comment in page textarea: %s", comment)
            self.comment_textarea.fill(comment)

        # 2. Click Reject button
        self.btn_reject.wait_for(state="visible", timeout=15000)
        self.btn_reject.click()

        # 3. If a modal dialog appears, enter comment and confirm
        try:
            if self.modal_comment_textarea.is_visible(timeout=3000):
                self.logger.info("Filling comment in modal textarea: %s", comment)
                self.modal_comment_textarea.fill(comment)
                if self.modal_btn_reject.is_visible():
                    self.modal_btn_reject.click()
        except Exception:
            pass

        self.page.wait_for_selector(".oxd-toast", timeout=15000)
        self.page.wait_for_load_state("networkidle")

    def approve_timesheet(self) -> None:
        """Supervisor approves the employee timesheet."""
        self.logger.info("Approving employee timesheet")
        self.btn_approve.wait_for(state="visible", timeout=15000)
        self.btn_approve.click()
        self.page.wait_for_selector(".oxd-toast", timeout=15000)
        self.page.wait_for_load_state("networkidle")

    def is_edit_locked(self) -> bool:
        """Returns True if the Edit button is locked/hidden/disabled (timesheet is finalized)."""
        try:
            if not self.btn_edit.is_visible():
                self.logger.info("Timesheet Edit button is not visible (locked=True)")
                return True
            is_disabled = self.btn_edit.is_disabled()
            self.logger.info("Timesheet Edit button disabled state: %s", is_disabled)
            return is_disabled
        except Exception as e:
            self.logger.warning("Exception checking edit button lock: %s", e)
            return True
