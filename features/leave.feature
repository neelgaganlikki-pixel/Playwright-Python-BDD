@leave
Feature: Leave Management
  As an OrangeHRM Administrator
  I want to view and filter the Leave List
  So that employee leave requests and statuses can be tracked efficiently

  @smoke
  Scenario: View Leave List and apply search filter
    Given the user is logged into the OrangeHRM portal
    When the user navigates to the Leave module
    And clicks the search button on the leave filter
    Then the leave results section should be displayed

  @regression
  Scenario: Reset leave search filter
    Given the user is logged into the OrangeHRM portal
    When the user navigates to the Leave module
    And clicks the reset button on the leave filter
    Then the leave results section should be displayed
