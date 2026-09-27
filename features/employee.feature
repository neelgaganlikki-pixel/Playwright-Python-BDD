@employee
Feature: Employee Management (PIM)
  As an HR Administrator
  I want to add new employees and search the employee records
  So that workforce information is up-to-date and easily accessible

  @smoke
  Scenario: Add a new employee successfully
    Given the user is logged into the OrangeHRM portal
    When the user navigates to the PIM module
    And clicks on the Add Employee tab
    And provides valid employee details
    And saves the employee
    Then the employee personal details page should be displayed

  @regression
  Scenario: Search for an existing employee by ID
    Given the user is logged into the OrangeHRM portal
    When the user navigates to the PIM module
    And retrieves an existing employee ID from the list
    And searches for the employee using that ID
    Then the employee record should be displayed in the results table
