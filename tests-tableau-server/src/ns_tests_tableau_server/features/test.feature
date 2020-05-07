Feature: basic smoke test
  
  Background: log into tableau server
    Given the user goes to the page https://glasscage-tableau.n-s.us/#/explore
    Then the user logs in

  Scenario: do something
    Given the user goes to the page https://glasscage-tableau.n-s.us/#/site/Testing/views/ericdefaultfunctions/Sheet1?:iid=1
    When the user clicks the edit tab

