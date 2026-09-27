@login
Feature: Authentication and Session Management
  As an OrangeHRM user
  I want to login with valid credentials and receive clear validation on invalid attempts
  So that I can securely access the HR management portal

  @smoke
  Scenario: Successful login with valid credentials
    Given the user navigates to the OrangeHRM login page
    When the user submits valid credentials
    Then the user should be redirected to the Dashboard page
    And the dashboard header should be displayed

  @regression
  Scenario: Unsuccessful login with invalid credentials
    Given the user navigates to the OrangeHRM login page
    When the user enters username "InvalidUser" and password "invalidPass123"
    And clicks the login button
    Then an error message stating "Invalid credentials" should be displayed

  @regression
  Scenario: Login validation with empty credentials
    Given the user navigates to the OrangeHRM login page
    When the user submits empty credentials
    Then input field validation message "Required" should be displayed

  @smoke
  Scenario: User logs out successfully
    Given the user is logged into the OrangeHRM portal
    When the user clicks the logout button
    Then the user should be redirected to the login page
