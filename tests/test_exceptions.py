"""Tests for lc2git.exceptions"""

from lc2git.exceptions import (
    LeetCodeAuthError, GitHubAuthError, MissingConfigError,
    LeetCodeAPIError, GitHubAPIError, RepoNotFoundError,
    RepoPermissionError, RateLimitError,
)


def test_leetcode_auth_error():
    e = LeetCodeAuthError()
    assert "expired" in str(e)
    assert "lc2git configure" in str(e)


def test_github_auth_error_with_detail():
    e = GitHubAuthError("403 Forbidden")
    assert "403 Forbidden" in str(e)


def test_missing_config_error():
    e = MissingConfigError("github_token")
    assert "github_token" in str(e)
    assert "lc2git configure" in str(e)


def test_repo_not_found_error():
    e = RepoNotFoundError("alice/leetcode")
    assert "alice/leetcode" in str(e)
    assert "github.com/new" in str(e)


def test_repo_permission_error():
    e = RepoPermissionError("alice/leetcode")
    assert "repo" in str(e)


def test_github_api_error():
    e = GitHubAPIError(404, "Not Found")
    assert "404" in str(e)


def test_rate_limit_error():
    e = RateLimitError("GitHub")
    assert "GitHub" in str(e)
