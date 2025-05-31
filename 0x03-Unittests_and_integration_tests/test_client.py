#!/usr/bin/env python3
"""Integration tests for client.GithubOrgClient.public_repos method."""

import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized_class
from client import GithubOrgClient # Assuming client.py contains GithubOrgClient
import fixtures # Assuming fixtures.py contains the payload data


@parameterized_class([{
    "org_payload": fixtures.org_payload,
    "repos_payload": fixtures.repos_payload,
    "expected_repos": fixtures.expected_repos,
    "apache2_repos": fixtures.apache2_repos,
}])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos."""

    @classmethod
    def setUpClass(cls):
        """Set up class fixtures before running tests."""
        # Ensure that org_payload (provided by @parameterized_class) is available
        # and contains the 'repos_url' key, as this is crucial for the mock setup.
        if not hasattr(cls, 'org_payload') or not isinstance(cls.org_payload, dict) or \
           "repos_url" not in cls.org_payload:
            raise ValueError(
                "Fixture 'org_payload' is missing, not a dictionary, or lacks 'repos_url'."
            )

        # Define the URL for the organization itself.
        # The client is instantiated with "google", so this URL is fixed.
        org_api_url = "https://api.github.com/orgs/google"
        
        # Define the URL for the repositories. This should come from the org_payload,
        # as a well-behaved client will use the `repos_url` provided by the API.
        repos_api_url_from_fixture = cls.org_payload["repos_url"]

        # This function will serve as the side_effect for the mocked requests.get
        def get_side_effect(url, *args, **kwargs):
            """Determines what the mocked requests.get(url) should return."""
            mock_response = Mock()
            mock_response.status_code = 200 # Default to 200 OK for matched URLs

            if url == org_api_url:
                mock_response.json.return_value = cls.org_payload
            elif url == repos_api_url_from_fixture: # Use the dynamic repos_url
                mock_response.json.return_value = cls.repos_payload
            else:
                # For any other URL, simulate a 404 Not Found.
                # This helps catch unexpected API calls made by the client.
                mock_response.status_code = 404
                # Making .json() raise an error for unmatched URLs can make debugging easier.
                mock_response.json.side_effect = ValueError(
                    f"Mock received unexpected URL: {url}. Expected {org_api_url} or {repos_api_url_from_fixture}"
                )
            return mock_response

        # Set up the patch for 'requests.get'
        cls.get_patcher = patch("requests.get")
        
        # Start the patcher. `start()` returns the mock object that replaces 'requests.get'.
        mock_requests_get = cls.get_patcher.start()
        
        # Assign our custom side_effect function to this mock object.
        mock_requests_get.side_effect = get_side_effect

    @classmethod
    def tearDownClass(cls):
        """Tear down class fixtures after all tests have run."""
        cls.get_patcher.stop() # Stop the patcher to restore original requests.get

    def test_public_repos(self):
        """Test that public_repos returns the expected list of repository names."""
        client_instance = GithubOrgClient("google")
        actual_repos = client_instance.public_repos()
        self.assertEqual(actual_repos, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test that public_repos correctly filters repositories by license."""
        client_instance = GithubOrgClient("google")
        repos = client_instance.public_repos(license_key="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)
