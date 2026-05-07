"""
config.py
Secure credential storage at ~/.config/lc2git/config.json (mode 600).

Priority order (highest → lowest):
    1. Environment variable
    2. Config file
    3. None / raise error
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from lc2git.exceptions import MissingConfigError

CONFIG_DIR  = Path.home() / ".config" / "lc2git"
CONFIG_FILE = CONFIG_DIR / "config.json"

ENV_MAP: dict[str, str] = {
    "github_token":     "GITHUB_TOKEN",
    "github_repo":      "GITHUB_REPO",
    "github_branch":    "GITHUB_BRANCH",
    "leetcode_session": "LEETCODE_SESSION",
    "leetcode_csrf":    "LEETCODE_CSRF_TOKEN",
}

SENSITIVE = {"github_token", "leetcode_session", "leetcode_csrf"}


def _load() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE) as f:
        return json.load(f)


def _save(data: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)
    os.chmod(CONFIG_FILE, 0o600)


def get(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a value — env var takes priority over config file."""
    env_var = ENV_MAP.get(key)
    if env_var:
        from_env = os.environ.get(env_var)
        if from_env:
            return from_env
    return _load().get(key, default)


def require(key: str) -> str:
    """Get a value or raise MissingConfigError."""
    value = get(key)
    if not value:
        raise MissingConfigError(key)
    return value


def set_value(key: str, value: str) -> None:
    data = _load()
    data[key] = value
    _save(data)


def set_many(values: dict[str, str]) -> None:
    data = _load()
    data.update(values)
    _save(data)


def delete(key: str) -> None:
    data = _load()
    data.pop(key, None)
    _save(data)


def all_values() -> dict:
    return _load()


def show() -> None:
    """Print config, masking sensitive values."""
    data = _load()
    if not data:
        print("No configuration found. Run `lc2git configure`.")
        return
    print(f"Config: {CONFIG_FILE}\n")
    for key, val in data.items():
        display = (val[:6] + "…" + val[-4:]) if key in SENSITIVE and len(val) > 10 else val
        print(f"  {key:<22} {display}")


# Convenience accessors
def github_token()     -> Optional[str]: return get("github_token")
def github_repo()      -> Optional[str]: return get("github_repo")
def github_branch()    -> str:           return get("github_branch") or "main"
def leetcode_session() -> Optional[str]: return get("leetcode_session")
def leetcode_csrf()    -> Optional[str]: return get("leetcode_csrf")
