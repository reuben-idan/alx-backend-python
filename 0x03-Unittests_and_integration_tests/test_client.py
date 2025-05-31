#!/usr/bin/env python3
"""Integration tests for client.GithubOrgClient.public_repos method."""

import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized_class # Ensure 'parameterized' library is installed
from client import GithubOrgClient # Assuming client.py contains GithubOrgClient
import fixtures # This will import your provided fixtures.py

# Extract the single test case's data from fixtures.TEST_PAYLOAD
# TEST_PAYLOAD is a list of tuples: [(org_payload, repos_payload, expected_repos, apache2_repos), ...]
# We are using the first (and only) test case defined in your fixtures.py
if not fixtures.TEST_PAYLOAD:
    raise ValueError("fixtures.TEST_PAYLOAD is empty. Cannot run tests.")

test_case_data = fixtures.TEST_PAYLOAD[0]
org_payload_fixture = test_case_data[0]
repos_payload_fixture = test_case_data[1]
expected_repos_fixture = test_case_data[2]
apache2_repos_fixture = test_case_data[3]


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
        # The client is instantiated with "google", so this URL is assumed fixed for these tests.
        cls.org_api_url = "https://api.github.com/orgs/google"
        
        # Define the URL for the repositories. This should come from the org_payload,
        # as a HATEOAS-compliant client will use the `repos_url` provided by the API.
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
                # If an unexpected URL is called, this helps in debugging.
                # print(f"DEBUG: URL_NOT_MATCHED: {url}. Expected {cls.org_api_url} or {cls.repos_api_url_from_fixture}")
                mock_response.status_code = 404 # Simulate Not Found
                mock_response.json.side_effect = ValueError(
                    f"Mock requests.get received unexpected URL: {url}. "
                    f"Expected one of [{cls.org_api_url}, {cls.repos_api_url_from_fixture}]"
                )
            return mock_response

        # Set up the patch for 'requests.get'.
        # This assumes 'client.py' uses 'requests.get()'. If 'GithubOrgClient'
        # is in 'client.py' and 'client.py' does 'import requests',
        # then 'client.requests.get' might be a more specific target.
        # However, we'll stick to "requests.get" as per the original problem context.
        cls.get_patcher = patch("requests.get")
        
        mock_requests_get = cls.get_patcher.start()
        mock_requests_get.side_effect = get_side_effect

    @classmethod
    def tearDownClass(cls):
        """Tear down class fixtures after all tests have run."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test that public_repos returns the expected list of repository names."""
        client_instance = GithubOrgClient("google")
        actual_repos = client_instance.public_repos()
        
        # print(f"DEBUG test_public_repos: Actual: {actual_repos}, Expected: {self.expected_repos}")
        self.assertEqual(actual_repos, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test that public_repos correctly filters repositories by license."""
        client_instance = GithubOrgClient("google")
        actual_repos_filtered = client_instance.public_repos(license_key="apache-2.0")

        # print(f"DEBUG test_public_repos_with_license: Actual: {actual_repos_filtered}, Expected: {self.apache2_repos}")
        self.assertEqual(actual_repos_filtered, self.apache2_repos)
