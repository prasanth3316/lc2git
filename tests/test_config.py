"""Tests for lc2git.config"""

import os
import json
import pytest
from pathlib import Path
from unittest.mock import patch

from lc2git import config
from lc2git.exceptions import MissingConfigError


@pytest.fixture(autouse=True)
def tmp_config(tmp_path, monkeypatch):
    """Redirect config file to a temp dir for every test."""
    monkeypatch.setattr(config, "CONFIG_DIR",  tmp_path)
    monkeypatch.setattr(config, "CONFIG_FILE", tmp_path / "config.json")
    yield


def test_get_returns_none_when_missing():
    assert config.get("github_token") is None


def test_set_and_get():
    config.set_value("github_token", "ghp_test123")
    assert config.get("github_token") == "ghp_test123"


def test_env_var_takes_priority(monkeypatch):
    config.set_value("github_token", "from_file")
    monkeypatch.setenv("GITHUB_TOKEN", "from_env")
    assert config.get("github_token") == "from_env"


def test_require_raises_when_missing():
    with pytest.raises(MissingConfigError):
        config.require("github_token")


def test_require_returns_value_when_set():
    config.set_value("github_token", "ghp_abc")
    assert config.require("github_token") == "ghp_abc"


def test_set_many():
    config.set_many({"github_token": "tok", "github_repo": "user/repo"})
    assert config.get("github_token") == "tok"
    assert config.get("github_repo")  == "user/repo"


def test_delete():
    config.set_value("github_token", "tok")
    config.delete("github_token")
    assert config.get("github_token") is None


def test_config_file_permissions():
    config.set_value("github_token", "tok")
    mode = config.CONFIG_FILE.stat().st_mode & 0o777
    assert mode == 0o600


def test_github_branch_default():
    assert config.github_branch() == "main"


def test_github_branch_custom():
    config.set_value("github_branch", "develop")
    assert config.github_branch() == "develop"
