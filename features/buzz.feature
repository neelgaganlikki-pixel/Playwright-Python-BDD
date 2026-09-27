@buzz
Feature: Buzz Social Media Feed
  As an OrangeHRM Employee
  I want to share status updates and view corporate announcements
  So that workplace collaboration and engagement are enhanced

  @smoke
  Scenario: Post a status update to Buzz newsfeed
    Given the user is logged into the OrangeHRM portal
    When the user navigates to the Buzz module
    And writes a new status update
    And clicks the post button
    Then the status update should appear in the Buzz newsfeed

  @regression
  Scenario: Verify Buzz feed loads existing posts
    Given the user is logged into the OrangeHRM portal
    When the user navigates to the Buzz module
    Then the Buzz newsfeed container should be displayed
