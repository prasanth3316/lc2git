"""GitHub client — creates/updates files in a target repository."""

from __future__ import annotations

import base64
from datetime import date
from typing import Optional

import requests

from .leetcode_client import Submission

API_BASE = "https://api.github.com"


class GitHubClient:
    def __init__(self, token: str, repo: str, branch: str = "main"):
        """
        :param token:  Personal Access Token (needs repo scope).
        :param repo:   Full repo name, e.g. 'alice/leetcode-solutions'.
        :param branch: Target branch (default: main).
        """
        self.repo = repo
        self.branch = branch
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    def _url(self, path: str) -> str:
        return f"{API_BASE}/repos/{self.repo}{path}"

    def whoami(self) -> str:
        """Validate token and return the authenticated GitHub username."""
        resp = self.session.get(f"{API_BASE}/user", timeout=10)
        resp.raise_for_status()
        return resp.json()["login"]

    def _get_file_sha(self, path: str) -> Optional[str]:
        """Return the blob SHA of an existing file, or None if not found."""
        resp = self.session.get(
            self._url(f"/contents/{path}"),
            params={"ref": self.branch},
            timeout=10,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json().get("sha")

    def push_file(self, path: str, content: str, commit_message: str) -> str:
        """
        Create or update a file at *path* in the repo.
        Returns the commit SHA.
        """
        encoded = base64.b64encode(content.encode()).decode()
        payload: dict = {
            "message": commit_message,
            "content": encoded,
            "branch": self.branch,
        }
        sha = self._get_file_sha(path)
        if sha:
            payload["sha"] = sha  # required for updates

        resp = self.session.put(self._url(f"/contents/{path}"), json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()["commit"]["sha"]

    def push_submission(self, sub: Submission) -> dict[str, str]:
        """
        Push a LeetCode submission to the repo.

        Directory layout:
            YYYY-MM-DD/
              0001-two-sum/
                solution.py
                README.md

        Returns a dict with paths of files pushed.
        """
        today = date.today().isoformat()
        base = f"{today}/{sub.folder_name}"

        # ── solution file ──────────────────────────────────────────────────────
        solution_path = f"{base}/{sub.file_name}"
        solution_content = _build_solution_header(sub) + sub.code
        commit_msg = (
            f"feat: add {sub.title} [{sub.difficulty}] — "
            f"{sub.runtime}, {sub.memory}"
        )
        sol_sha = self.push_file(solution_path, solution_content, commit_msg)

        # ── README ─────────────────────────────────────────────────────────────
        readme_path = f"{base}/README.md"
        readme_content = _build_readme(sub)
        self.push_file(readme_path, readme_content, f"docs: add README for {sub.title}")

        return {"solution": solution_path, "readme": readme_path, "commit": sol_sha}


# ── File content builders ──────────────────────────────────────────────────────

def _build_solution_header(sub: Submission) -> str:
    tags = ", ".join(sub.tags) if sub.tags else "N/A"
    return (
        f"# {sub.title}\n"
        f"# Difficulty : {sub.difficulty}\n"
        f"# Tags       : {tags}\n"
        f"# Runtime    : {sub.runtime}\n"
        f"# Memory     : {sub.memory}\n"
        f"# Link       : https://leetcode.com/problems/{sub.title_slug}/\n\n"
    )


def _build_readme(sub: Submission) -> str:
    tags_md = " ".join(f"`{t}`" for t in sub.tags) if sub.tags else "N/A"
    return f"""# {sub.question_id}. {sub.title}

| Field | Value |
|-------|-------|
| Difficulty | {sub.difficulty} |
| Tags | {tags_md} |
| Runtime | {sub.runtime} |
| Memory | {sub.memory} |
| Language | {sub.lang} |

🔗 [LeetCode Problem](https://leetcode.com/problems/{sub.title_slug}/)

## Notes

<!-- Add your notes / approach here -->
"""
