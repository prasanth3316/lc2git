"""
lc2git — sync your LeetCode solutions to GitHub.

Usage:
    lc2git configure          # save credentials
    lc2git sync               # push today's solutions
    lc2git sync --all         # push all solutions
    lc2git stats              # your stats
    lc2git info <username>    # any public user's stats
"""

from lc2git._version import __version__, __author__, __license__

__all__ = ["__version__", "__author__", "__license__"]
