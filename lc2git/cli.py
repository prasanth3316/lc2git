"""
cli.py — lc2git command line interface.
Phase 1: configure + show-config only.
Sync commands added in Phase 4.
"""

import getpass
import os

import click

from lc2git._version import __version__
from lc2git import config
from lc2git.sync import run_sync


@click.group()
@click.version_option(__version__, prog_name="lc2git")
def main():
    """lc2git — sync your LeetCode solutions to GitHub."""


@main.command()
@click.option("--github-token",     default=None, help="GitHub Personal Access Token")
@click.option("--github-repo",      default=None, help="Target repo e.g. alice/leetcode")
@click.option("--github-branch",    default=None, help="Branch (default: main)")
@click.option("--leetcode-session", default=None, help="LEETCODE_SESSION cookie")
@click.option("--leetcode-csrf",    default=None, help="csrftoken cookie")
def configure(github_token, github_repo, github_branch, leetcode_session, leetcode_csrf):
    """Save credentials to ~/.config/lc2git/config.json"""
    click.echo("lc2git — Configuration\n")

    gh_token  = github_token  or _prompt_secret("GitHub Personal Access Token", "GITHUB_TOKEN")
    gh_repo   = github_repo   or click.prompt("GitHub repo (e.g. alice/leetcode-solutions)")
    gh_branch = github_branch or click.prompt("Branch", default="main")

    click.echo(
        "\nTo get your LeetCode cookies:\n"
        "  1. Log in at https://leetcode.com\n"
        "  2. Open DevTools (⌘⌥I) → Application → Cookies → leetcode.com\n"
        "  3. Copy LEETCODE_SESSION and csrftoken\n"
    )
    lc_session = leetcode_session or _prompt_secret("LEETCODE_SESSION cookie", "LEETCODE_SESSION")
    lc_csrf    = leetcode_csrf    or _prompt_secret("csrftoken cookie",        "LEETCODE_CSRF_TOKEN")

    config.set_many({
        "github_token":     gh_token,
        "github_repo":      gh_repo,
        "github_branch":    gh_branch,
        "leetcode_session": lc_session,
        "leetcode_csrf":    lc_csrf,
    })

    click.echo(f"\n✅  Config saved to {config.CONFIG_FILE}")
    click.echo("    Run `lc2git sync` to push your solutions.")


@main.command("show-config")
def show_config():
    """Print current configuration (tokens are masked)."""
    config.show()


@main.command()
@click.option("--limit", default=50, help="Max submissions to check (default: 50)")
@click.option("--dry-run", is_flag=True, help="Validate but don't push to GitHub")
def sync(limit, dry_run):
    """Fetch today's LeetCode solutions and push to GitHub."""
    try:
        if dry_run:
            click.echo("🔍 Running in dry-run mode (no files will be pushed)\n")
        run_sync(limit=limit, dry_run=dry_run)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Exit(1)


def _prompt_secret(label: str, env_var: str) -> str:
    from_env = os.environ.get(env_var)
    if from_env:
        click.echo(f"{label}: (read from ${env_var})")
        return from_env
    return getpass.getpass(f"{label}: ")
