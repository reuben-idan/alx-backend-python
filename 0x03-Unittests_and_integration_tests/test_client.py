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
        # Validate that org_payload (provided by @parameterized_class) is available
        # and contains the 'repos_url' key, as this is crucial for the mock setup.
        if not hasattr(cls, 'org_payload') or not isinstance(cls.org_payload, dict) or \
           "repos_url" not in cls.org_payload:
            # This error would typically indicate an issue with the fixture data
            # or how parameterized_class is populating class attributes.
            raise ValueError(
                "org_payload fixture is missing, not a dictionary, or lacks 'repos_url'."
            )

        # Define the URLs that the mock for requests.get should respond to.
        # The primary organization API URL.
        org_api_url = "https://api.github.com/orgs/google"
        
        # The repositories API URL is dynamically obtained from the org_payload fixture.
        # This is the key change to make the mock robust to the actual repos_url
        # that the client will use (which it gets from the org_payload).
        repos_api_url = cls.org_payload["repos_url"]

        # This function will serve as the side_effect for the mocked requests.get
        def get_side_effect(url, *args, **kwargs):
            """Determines what the mocked requests.get(url) should return."""
            mock_response = Mock()
            # print(f"DEBUG: Mock requests.get called with URL: {url}") # Uncomment for debugging

            if url == org_api_url:
                mock_response.json.return_value = cls.org_payload
                mock_response.status_code = 200 # Good practice to mock status_code
            elif url == repos_api_url:
                mock_response.json.return_value = cls.repos_payload
                mock_response.status_code = 200 # Good practice to mock status_code
            else:
                # For any other URL, return a 404-like response.
                # The client code under test would ideally handle such cases.
                # If client calls .json() on this, it will get a new Mock (default behavior of Mock)
                # or raise an error if mock_response.json.side_effect were set to an Exception.
                mock_response.status_code = 404
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
        # Instantiate the client (org name "google" is fixed for these tests)
        client_instance = GithubOrgClient("google")
        # Call the method under test
        actual_repos = client_instance.public_repos()
        # Assert that the returned repositories match the expected fixture data
        # self.expected_repos is provided by @parameterized_class
        self.assertEqual(actual_repos, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test that public_repos correctly filters repositories by license."""
        client_instance = GithubOrgClient("google")
        # Call the method under test with a specific license key
        actual_repos = client_instance.public_repos(license_key="apache-2.0")
        # Assert that the returned repositories match the expected fixture data
        # self.apache2_repos is provided by @parameterized_class
        self.assertEqual(actual_repos, self.apache2_repos)
