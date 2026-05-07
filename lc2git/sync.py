"""Orchestrates fetching from LeetCode and pushing to GitHub."""

from __future__ import annotations

from typing import Optional

from . import config
from .github_client import GitHubClient
from .leetcode_client import LeetCodeClient


def run_sync(
    *,
    lc_session: Optional[str] = None,
    lc_csrf: Optional[str] = None,
    gh_token: Optional[str] = None,
    gh_repo: Optional[str] = None,
    gh_branch: Optional[str] = None,
    limit: int = 50,
    dry_run: bool = False,
) -> None:
    """
    Main sync entry point.
    Falls back to stored config when individual params are not provided.
    """
    lc_session = lc_session or config.get("leetcode_session")
    lc_csrf    = lc_csrf    or config.get("leetcode_csrf")
    gh_token   = gh_token   or config.get("github_token")
    gh_repo    = gh_repo    or config.get("github_repo")
    gh_branch  = gh_branch  or config.get("github_branch", "main")

    _require("LeetCode session cookie", lc_session)
    _require("LeetCode CSRF token",     lc_csrf)
    _require("GitHub token",            gh_token)
    _require("GitHub repo",             gh_repo)

    # ── validate credentials ───────────────────────────────────────────────────
    print("🔐  Validating credentials…")
    lc = LeetCodeClient(lc_session, lc_csrf)
    lc_username = lc.whoami()
    print(f"    LeetCode  → {lc_username}")

    gh = GitHubClient(gh_token, gh_repo, gh_branch)
    gh_username = gh.whoami()
    print(f"    GitHub    → {gh_username}  (repo: {gh_repo}, branch: {gh_branch})")

    # ── fetch today's submissions ──────────────────────────────────────────────
    print("\n📥  Fetching today's accepted submissions…")
    submissions = lc.get_todays_submissions(lc_username)

    if not submissions:
        print("    No accepted submissions found for today. Nothing to push.")
        return

    print(f"    Found {len(submissions)} submission(s):\n")
    for s in submissions:
        print(f"    • [{s.difficulty:6}] {s.title}  ({s.lang})")

    if dry_run:
        print("\n🔍  Dry-run mode — skipping GitHub push.")
        return

    # ── push to GitHub ─────────────────────────────────────────────────────────
    print("\n🚀  Pushing to GitHub…")
    for sub in submissions:
        print(f"    Uploading {sub.title}… ", end="", flush=True)
        result = gh.push_submission(sub)
        print(f"✓  (commit {result['commit'][:7]})")

    print(f"\n✅  Done! {len(submissions)} solution(s) pushed to {gh_repo}.")


def _require(label: str, value) -> None:
    if not value:
        raise ValueError(
            f"Missing {label}. Run `lc2git configure` or set the corresponding "
            f"environment variable."
        )
