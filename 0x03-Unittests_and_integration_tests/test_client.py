#!/usr/bin/env python3
"""Integration and unit tests for client.GithubOrgClient."""

import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized_class # Ensure 'parameterized' library is installed
from client import GithubOrgClient # Assuming client.py contains GithubOrgClient
import fixtures # Import the whole fixtures module

# --- Robust extraction of test case data from fixtures.TEST_PAYLOAD ---
# TEST_PAYLOAD is expected to be a list of tuples:
# [(org_payload_dict, repos_payload_list, expected_repos_list, apache2_repos_list), ...]
# We are using the first (and only, as per the provided fixtures.py) test case.

if not hasattr(fixtures, 'TEST_PAYLOAD') or \
   not fixtures.TEST_PAYLOAD or \
   not isinstance(fixtures.TEST_PAYLOAD, list) or \
   len(fixtures.TEST_PAYLOAD) == 0 or \
   not fixtures.TEST_PAYLOAD[0] or \
   not isinstance(fixtures.TEST_PAYLOAD[0], tuple):
    raise ValueError(
        "fixtures.TEST_PAYLOAD is missing, empty, not a list, "
        "or its first element is not a tuple. Cannot run tests."
    )

if len(fixtures.TEST_PAYLOAD[0]) < 4:
    raise ValueError(
        "fixtures.TEST_PAYLOAD[0] does not contain enough elements. "
        "Expected at least 4 (org_payload, repos_payload, expected_repos, apache2_repos)."
    )

# These variables will be used by @parameterized_class
org_payload_data = fixtures.TEST_PAYLOAD[0][0]
repos_payload_data = fixtures.TEST_PAYLOAD[0][1]
expected_repos_data = fixtures.TEST_PAYLOAD[0][2]
apache2_repos_data = fixtures.TEST_PAYLOAD[0][3]
# --- End of fixture data extraction ---


@parameterized_class([{
    "org_payload": org_payload_data,
    "repos_payload": repos_payload_data,
    "expected_repos": expected_repos_data,
    "apache2_repos": apache2_repos_data,
}])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos."""

    @classmethod
    def setUpClass(cls):
        """Patch requests.get and mock JSON responses based on dynamic URLs."""
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
            
            if url == cls.org_api_url:
                mock_response.json.return_value = cls.org_payload
                mock_response.status_code = 200
            elif url == cls.repos_api_url_from_fixture: # Use the dynamic repos_url
                mock_response.json.return_value = cls.repos_payload
                mock_response.status_code = 200
            else:
                # If an unexpected URL is called by the client:
                mock_response.status_code = 404 # Simulate Not Found
                mock_response.json.side_effect = ValueError(
                    f"Mock requests.get received unexpected URL: {url}. "
                    f"Expected one of [{cls.org_api_url}, {cls.repos_api_url_from_fixture}]"
                )
            return mock_response

        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()
        mock_get.side_effect = get_side_effect
        cls.mock_requests_get = mock_get # Store for debugging if needed

    @classmethod
    def tearDownClass(cls):
        """Stop patching requests.get."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test that public_repos returns the expected list of repos."""
        client = GithubOrgClient("google")
        # Use assertCountEqual for lists where order might not be guaranteed
        self.assertCountEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test that public_repos filters repos by license 'apache-2.0'."""
        client = GithubOrgClient("google")
        repos = client.public_repos(license_key="apache-2.0")
        # Use assertCountEqual for lists where order might not be guaranteed
        self.assertCountEqual(repos, self.apache2_repos)

if __name__ == '__main__':
    unittest.main()
