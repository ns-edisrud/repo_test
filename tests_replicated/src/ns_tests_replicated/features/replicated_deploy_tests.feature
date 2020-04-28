@tests-replicated
Feature: Tests for Replicated deployment

  Scenario: Validate the correct version is installed
    Given a version request is sent to the replicated test stack
    Then a 200 response is returned
    And the viz-server version is "0.18.0"

  Scenario: Basic health check (story write)
    Given the test data is retrieved from S3
    When a story request is sent to v2/stories/scatterplot
    Then a 200 response is returned
    And the response content header should be HTML

  Scenario Outline: Validate viz extensions are reachable
    Given the viz extension <extension> is polled
    Then a 200 response is returned
    Examples: Extensions
      | extension          |
      | tableau-add-in/0.0 |
      | qlik-sense/1.0     |
      | powerbi/0.0        |
