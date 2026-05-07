"""LeetCode API client using the unofficial GraphQL endpoint."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional

import requests

GRAPHQL_URL = "https://leetcode.com/graphql"

LANG_EXT: dict[str, str] = {
    "python3": "py",
    "python": "py",
    "java": "java",
    "cpp": "cpp",
    "c": "c",
    "csharp": "cs",
    "javascript": "js",
    "typescript": "ts",
    "go": "go",
    "rust": "rs",
    "kotlin": "kt",
    "swift": "swift",
    "scala": "scala",
    "ruby": "rb",
    "php": "php",
    "mysql": "sql",
    "postgresql": "sql",
    "bash": "sh",
}

RECENT_SUBMISSIONS_QUERY = """
query recentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    id
    title
    titleSlug
    timestamp
    lang
  }
}
"""

SUBMISSION_DETAIL_QUERY = """
query submissionDetails($submissionId: Int!) {
  submissionDetails(submissionId: $submissionId) {
    code
    timestamp
    lang {
      name
    }
    question {
      questionId
      title
      titleSlug
      difficulty
      topicTags {
        name
      }
    }
    runtimeDisplay
    memoryDisplay
    statusDisplay
  }
}
"""

QUESTION_DETAIL_QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId
    title
    difficulty
    content
    topicTags {
      name
    }
  }
}
"""


@dataclass
class Submission:
    submission_id: str
    title: str
    title_slug: str
    timestamp: int
    lang: str
    code: str
    question_id: str
    difficulty: str
    tags: List[str]
    runtime: str
    memory: str

    @property
    def ext(self) -> str:
        return LANG_EXT.get(self.lang.lower(), "txt")

    @property
    def folder_name(self) -> str:
        """e.g. '0001-two-sum'"""
        return f"{int(self.question_id):04d}-{self.title_slug}"

    @property
    def file_name(self) -> str:
        return f"solution.{self.ext}"


class LeetCodeClient:
    def __init__(self, session_cookie: str, csrf_token: str):
        self.session = requests.Session()
        self.session.cookies.set("LEETCODE_SESSION", session_cookie, domain="leetcode.com")
        self.session.cookies.set("csrftoken", csrf_token, domain="leetcode.com")
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Referer": "https://leetcode.com",
                "x-csrftoken": csrf_token,
            }
        )

    def _gql(self, query: str, variables: dict) -> dict:
        resp = self.session.post(
            GRAPHQL_URL, json={"query": query, "variables": variables}, timeout=15
        )
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            raise RuntimeError(f"GraphQL error: {data['errors']}")
        return data["data"]

    def whoami(self) -> str:
        """Return the authenticated username (validates credentials)."""
        query = "query { userStatus { username } }"
        data = self._gql(query, {})
        username = data.get("userStatus", {}).get("username")
        if not username:
            raise ValueError("Invalid LeetCode credentials — could not fetch username.")
        return username

    def get_recent_accepted(self, username: str, limit: int = 20) -> List[dict]:
        """Return lightweight submission stubs (no code yet)."""
        data = self._gql(
            RECENT_SUBMISSIONS_QUERY, {"username": username, "limit": limit}
        )
        return data.get("recentAcSubmissionList", [])

    def get_submission_detail(self, submission_id: str) -> Optional[Submission]:
        """Fetch full code + metadata for one submission."""
        try:
            data = self._gql(
                SUBMISSION_DETAIL_QUERY, {"submissionId": int(submission_id)}
            )
            detail = data.get("submissionDetails")
            if not detail:
                return None

            q = detail["question"]
            return Submission(
                submission_id=submission_id,
                title=q["title"],
                title_slug=q["titleSlug"],
                timestamp=int(detail["timestamp"]),
                lang=detail["lang"]["name"],
                code=detail["code"],
                question_id=q["questionId"],
                difficulty=q["difficulty"],
                tags=[t["name"] for t in q.get("topicTags", [])],
                runtime=detail.get("runtimeDisplay", "N/A"),
                memory=detail.get("memoryDisplay", "N/A"),
            )
        except Exception as exc:
            print(f"  ⚠ Could not fetch details for submission {submission_id}: {exc}")
            return None

    def get_todays_submissions(self, username: str) -> List[Submission]:
        """
        Return full Submission objects for all accepted solutions submitted today.
        Deduplicates by question — keeps the most recent submission per problem.
        """
        today_start = _today_unix()
        stubs = self.get_recent_accepted(username, limit=50)

        seen_slugs: set[str] = set()
        results: List[Submission] = []

        for stub in stubs:
            ts = int(stub["timestamp"])
            if ts < today_start:
                break  # stubs are newest-first; stop when we hit yesterday

            slug = stub["titleSlug"]
            if slug in seen_slugs:
                continue  # already have a newer submission for this problem
            seen_slugs.add(slug)

            time.sleep(0.5)  # be polite to the API
            detail = self.get_submission_detail(stub["id"])
            if detail:
                results.append(detail)

        return results


def _today_unix() -> int:
    """Unix timestamp for midnight (00:00:00) today in local time."""
    import datetime

    today = datetime.date.today()
    midnight = datetime.datetime(today.year, today.month, today.day)
    return int(midnight.timestamp())
