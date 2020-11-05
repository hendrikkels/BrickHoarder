Feature: Dashboard
  """
      Dashboard feature will test for loading and cached dashboard results.
  """

  Scenario: Loading data test for dashboard
    Given I navigate to dashboard page
    And Data is still being fetched
    Then Dashboard shows loading data

  Scenario: Cached data test for dashboard
    Given I navigate to dashboard page
    And Data in cache variables are not None
    Then Dashboard shows price data

