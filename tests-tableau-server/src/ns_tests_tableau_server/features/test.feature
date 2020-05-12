Feature: basic smoke test

  @setup
  Scenario: Setup
    Given the user goes to the page https://glasscage-tableau.n-s.us/#/explore
    Then the user logs in

  Scenario: do something
    Given the user goes to the page https://glasscage-tableau.n-s.us/t/Testing/authoring/ericdefaultfunctions/2x1continuousfunctions#1
    Then the user opens the edit story modal
    Then the user is on the edit story page
    When the user clicks on the add custom story item button
    Then the user enters "hello hello" into the custom content box
    Then I wait 10 seconds