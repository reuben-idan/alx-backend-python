#!/usr/bin/env python3
"""Integration tests for client.GithubOrgClient.public_repos method."""

import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized_class # Ensure 'parameterized' library is installed
from client import GithubOrgClient # Assuming client.py contains GithubOrgClient
import fixtures # This will import your provided fixtures.py

# --- Robust extraction of test case data from fixtures.TEST_PAYLOAD ---
# TEST_PAYLOAD is expected to be a list of tuples:
# [(org_payload, repos_payload, expected_repos, apache2_repos), ...]
# We are using the first (and only, as per example) test case.

if not fixtures.TEST_PAYLOAD or not isinstance(fixtures.TEST_PAYLOAD, list) or \
   len(fixtures.TEST_PAYLOAD) == 0 or \
   not fixtures.TEST_PAYLOAD[0] or not isinstance(fixtures.TEST_PAYLOAD[0], tuple):
    raise ValueError(
        "fixtures.TEST_PAYLOAD is empty, not a list, or its first element is not a tuple. "
        "Cannot run tests."
    )

if len(fixtures.TEST_PAYLOAD[0]) < 4:
    raise ValueError(
        "fixtures.TEST_PAYLOAD[0] does not contain enough elements. "
        "Expected at least 4 (org_payload, repos_payload, expected_repos, apache2_repos)."
    )

test_case_data = fixtures.TEST_PAYLOAD[0]
org_payload_fixture = test_case_data[0]
repos_payload_fixture = test_case_data[1]
expected_repos_fixture = test_case_data[2]
apache2_repos_fixture = test_case_data[3]
# --- End of fixture data extraction ---


@parameterized_class([{
    "org_payload": org_payload_fixture,
    "repos_payload": repos_payload_fixture,
    "expected_repos": expected_repos_fixture,
    "apache2_repos": apache2_repos_fixture,
}])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos."""

    @classmethod
    def setUpClass(cls):
        """Set up class fixtures before running tests."""
        # Ensure that org_payload (from @parameterized_class via fixtures) is available
        # and contains the 'repos_url' key, as this is crucial for the mock setup.
        if not hasattr(cls, 'org_payload') or not isinstance(cls.org_payload, dict) or \
           "repos_url" not in cls.org_payload:
            raise AttributeError(
                "Class attribute 'org_payload' is missing, not a dictionary, or lacks 'repos_url'. "
                "Check @parameterized_class setup and fixtures.py."
            )

        # Define the URL for the organization itself.
        cls.org_api_url = "https://api.github.com/orgs/google" # Client instantiated with "google"
        
        # Define the URL for the repositories, dynamically from the org_payload.
        cls.repos_api_url_from_fixture = cls.org_payload["repos_url"]

        # This function will serve as the side_effect for the mocked requests.get
        def get_side_effect(url, *args, **kwargs):
            """Determines what the mocked requests.get(url) should return."""
            mock_response = Mock()
            # print(f"DEBUG: Mock requests.get called with URL: {url}") # Uncomment for debugging

            if url == cls.org_api_url:
                # print(f"DEBUG: Matched org_api_url: {cls.org_api_url}")
                mock_response.json.return_value = cls.org_payload
                mock_response.status_code = 200
            elif url == cls.repos_api_url_from_fixture: # Use the dynamic repos_url
                # print(f"DEBUG: Matched repos_api_url_from_fixture: {cls.repos_api_url_from_fixture}")
                mock_response.json.return_value = cls.repos_payload
                mock_response.status_code = 200
            else:
                # If an unexpected URL is called by the client:
                # print(f"DEBUG: URL_NOT_MATCHED: {url}. Expected {cls.org_api_url} or {cls.repos_api_url_from_fixture}")
                mock_response.status_code = 404 # Simulate Not Found
                # Make .json() raise an error for easier debugging if client tries to parse this
                mock_response.json.side_effect = ValueError(
                    f"Mock requests.get received unexpected URL: {url}. "
                    f"Expected one of [{cls.org_api_url}, {cls.repos_api_url_from_fixture}]"
                )
            return mock_response

        # Set up the patch for 'requests.get'.
        # This assumes 'client.py' (where GithubOrgClient is) uses 'requests.get()'.
        cls.get_patcher = patch("requests.get")
        
        mock_requests_get = cls.get_patcher.start()
        mock_requests_get.side_effect = get_side_effect
        # Store mock for potential debugging access in test methods
        cls.mock_requests_get = mock_requests_get 

    @classmethod
    def tearDownClass(cls):
        """Tear down class fixtures after all tests have run."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """
        Test that GithubOrgClient.public_repos returns the expected list of 
        repository names based on the fixtures, without any license filter.
        """
        # Instantiate the client for the 'google' organization
        client_instance = GithubOrgClient("google")
        
        # Call the method under test
        actual_repos = client_instance.public_repos()
        
        # For debugging if this test fails:
        # print(f"\nDEBUG test_public_repos:")
        # print(f"  Actual (len {len(actual_repos)}):   {actual_repos}")
        # print(f"  Expected (len {len(self.expected_repos)}): {self.expected_repos}")
        # print(f"  Mock calls to requests.get: {self.mock_requests_get.call_args_list}")
        
        # Assert that the actual list of repo names matches the expected list from fixtures.
        # assertCountEqual is used because the order of repository names might not be guaranteed.
        self.assertCountEqual(actual_repos, self.expected_repos)

    def test_public_repos_with_license(self):
        """
        Test that GithubOrgClient.public_repos with license="apache-2.0"
        returns the expected list of repository names filtered by that license,
        based on the fixtures.
        """
        # Instantiate the client for the 'google' organization
        client_instance = GithubOrgClient("google")
        
        # Call the method under test with the specified license key
        license_to_test = "apache-2.0"
        actual_repos_filtered = client_instance.public_repos(license_key=license_to_test)

        # For debugging if this test fails:
        # print(f"\nDEBUG test_public_repos_with_license (license: {license_to_test}):")
        # print(f"  Actual (filtered) (len {len(actual_repos_filtered)}): {actual_repos_filtered}")
        # print(f"  Expected (apache2) (len {len(self.apache2_repos)}): {self.apache2_repos}")
        # print(f"  Mock calls to requests.get: {self.mock_requests_get.call_args_list}")

        # Assert that the actual list of filtered repo names matches the expected list from fixtures.
        # assertCountEqual is used because the order of repository names might not be guaranteed.
        self.assertCountEqual(actual_repos_filtered, self.apache2_repos)

if __name__ == '__main__':
    unittest.main()
