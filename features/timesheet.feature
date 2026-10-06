@timesheet
Feature: Time and Attendance - Weekly Timesheet Lifecycle
  As an OrangeHRM Employee and Supervisor
  I want to submit, review, reject with comments, revise, and approve weekly timesheets
  So that project hours are accurately tracked and audited

  @regression
  Scenario: Weekly Timesheet Submission, Rejection, Revision, and Approval
    Given an employee is registered with a reporting supervisor
    When the employee logs in and navigates to My Timesheets
    And the employee enters project "Apache" and logs 8 hours from Monday to Friday
    And saves and submits the timesheet
    Then the timesheet status should display "Submitted"
    When the supervisor logs in and reviews the employee timesheet
    And rejects the timesheet with comment "Please correct Wednesday hours"
    Then the timesheet status should display "Rejected"
    When the employee logs in and views their timesheet
    Then the timesheet status should display "Rejected"
    When the employee updates Wednesday hours to 7.00 and re-submits the timesheet
    Then the timesheet status should display "Submitted"
    When the supervisor reviews the employee timesheet and clicks approve
    Then the timesheet status should display "Approved"
    And the timesheet should be locked from further employee edits

