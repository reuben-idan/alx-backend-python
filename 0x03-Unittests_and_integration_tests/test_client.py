#!/usr/bin/env python3
"""Integration tests for client.GithubOrgClient.public_repos."""

import unittest
from unittest.mock import patch
from parameterized import parameterized_class
from client import GithubOrgClient
import fixtures


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    [
        (
            fixtures.org_payload,
            fixtures.repos_payload,
            fixtures.expected_repos,
            fixtures.apache2_repos,
        ),
    ],
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test for GithubOrgClient.public_repos."""

    def setUp(self):
        """Start patching requests.get as instance attribute."""
        self.get_patcher = patch("client.requests.get")
        self.mock_get = self.get_patcher.start()

        def side_effect(url, *args, **kwargs):
            class MockResponse:
                def __init__(self, json_data):
                    self._json = json_data

                def json(self):
                    return self._json

            if url == "https://api.github.com/orgs/google":
                return MockResponse(self.org_payload)
            if url == "https://api.github.com/orgs/google/repos":
                return MockResponse(self.repos_payload)
            return MockResponse(None)

        self.mock_get.side_effect = side_effect

    def tearDown(self):
        """Stop patching requests.get."""
        self.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns expected repo list."""
        client = GithubOrgClient("google")
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos filtered by license_key returns expected repos."""
        client = GithubOrgClient("google")
        repos = client.public_repos(license_key="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)
