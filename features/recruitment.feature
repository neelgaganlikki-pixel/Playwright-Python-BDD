@recruitment
Feature: Recruitment and Candidate Management
  As a Recruitment Specialist
  I want to review candidates and add new applicants
  So that hiring pipelines can be tracked and managed

  @smoke
  Scenario: View candidate list in recruitment module
    Given the user is logged into the OrangeHRM portal
    When the user navigates to the Recruitment module
    Then the candidate records list should be visible

  @smoke
  Scenario: Add a new candidate successfully
    Given the user is logged into the OrangeHRM portal
    When the user navigates to the Recruitment module
    And clicks on the Add Candidate button
    And enters candidate details
    And saves the candidate
    Then the candidate application details should be displayed
