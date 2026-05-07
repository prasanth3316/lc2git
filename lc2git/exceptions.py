"""
exceptions.py
All custom exceptions for lc2git — clean, descriptive errors
instead of raw Python/requests tracebacks.
"""


class Lc2GitError(Exception):
    """Base exception for all lc2git errors."""


# ── Auth errors ────────────────────────────────────────────────────────────────

class AuthError(Lc2GitError):
    """Raised when credentials are missing or invalid."""


class LeetCodeAuthError(AuthError):
    """LeetCode session cookie is expired or invalid."""
    def __init__(self):
        super().__init__(
            "LeetCode authentication failed.\n"
            "Your session cookie may have expired.\n"
            "Run `lc2git configure` to update your credentials."
        )


class GitHubAuthError(AuthError):
    """GitHub token is invalid or missing required scopes."""
    def __init__(self, detail: str = ""):
        msg = "GitHub authentication failed."
        if detail:
            msg += f" ({detail})"
        msg += "\nRun `lc2git configure` to update your token."
        super().__init__(msg)


# ── Config errors ──────────────────────────────────────────────────────────────

class ConfigError(Lc2GitError):
    """Raised when required config values are missing."""


class MissingConfigError(ConfigError):
    """A required config key has not been set."""
    def __init__(self, key: str):
        super().__init__(
            f"Missing config: '{key}'.\n"
            f"Run `lc2git configure` to set it."
        )


# ── API errors ─────────────────────────────────────────────────────────────────

class APIError(Lc2GitError):
    """Raised when an API call fails unexpectedly."""


class LeetCodeAPIError(APIError):
    """LeetCode GraphQL API returned an error."""
    def __init__(self, message: str):
        super().__init__(f"LeetCode API error: {message}")


class GitHubAPIError(APIError):
    """GitHub REST API returned an error."""
    def __init__(self, status: int, message: str):
        super().__init__(f"GitHub API error {status}: {message}")


class RateLimitError(APIError):
    """API rate limit hit."""
    def __init__(self, service: str = "API"):
        super().__init__(
            f"{service} rate limit reached. Wait a moment and try again."
        )


# ── Repo errors ────────────────────────────────────────────────────────────────

class RepoError(Lc2GitError):
    """Raised for GitHub repo problems."""


class RepoNotFoundError(RepoError):
    """Target GitHub repo does not exist."""
    def __init__(self, repo: str):
        super().__init__(
            f"GitHub repo '{repo}' not found.\n"
            f"Create it at https://github.com/new — remember to add a README."
        )


class RepoPermissionError(RepoError):
    """Token does not have write access to the repo."""
    def __init__(self, repo: str):
        super().__init__(
            f"No write access to '{repo}'.\n"
            f"Make sure your token has the 'repo' scope checked."
        )
