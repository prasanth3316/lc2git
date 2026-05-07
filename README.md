# lc2git 🚀

> Push your daily LeetCode solutions to GitHub automatically — one command.

## Features

- Fetches **all accepted submissions from today** (deduplicates per problem)
- Organises files by date & problem: `YYYY-MM-DD/0001-two-sum/solution.py`
- Auto-generates a **README.md** per problem with difficulty, tags, runtime & memory
- Adds a language-specific **header comment** to every solution file
- Supports **20+ languages** (Python, Java, C++, Go, Rust, TypeScript, …)
- Credentials stored securely at `~/.config/lc2git/config.json` (mode 600)
- All secrets can also be passed via **environment variables**

## Installation

```bash
pip install lc2git
```

Or install from source:

```bash
git clone https://github.com/you/lc2git.git
cd lc2git
pip install -e .
```

## Quick Start

### 1. Configure credentials

```bash
lc2git configure
```

You'll be prompted for:

| Field | Where to find it |
|-------|-----------------|
| **GitHub PAT** | github.com → Settings → Developer settings → Personal access tokens → (needs `repo` scope) |
| **GitHub repo** | e.g. `alice/leetcode-solutions` (must already exist) |
| **LEETCODE_SESSION** | leetcode.com → DevTools → Application → Cookies → `LEETCODE_SESSION` |
| **csrftoken** | Same cookie jar → `csrftoken` |

### 2. Sync today's solutions

```bash
lc2git sync
```

### 3. Preview without pushing

```bash
lc2git sync --dry-run
```

## Output Layout

```
2025-05-07/
  0001-two-sum/
    solution.py        ← your code + header comment
    README.md          ← problem metadata
  0042-trapping-rain-water/
    solution.cpp
    README.md
```

### Example solution file

```python
# Two Sum
# Difficulty : Easy
# Tags       : Array, Hash Table
# Runtime    : 52 ms
# Memory     : 16.4 MB
# Link       : https://leetcode.com/problems/two-sum/

class Solution:
    def twoSum(self, nums, target):
        seen = {}
        for i, n in enumerate(nums):
            if target - n in seen:
                return [seen[target - n], i]
            seen[n] = i
```

## Environment Variables

All credentials can be provided via environment variables (useful for CI):

```bash
export GITHUB_TOKEN=ghp_...
export GITHUB_REPO=alice/leetcode-solutions
export GITHUB_BRANCH=main
export LEETCODE_SESSION=eyJ...
export LEETCODE_CSRF_TOKEN=abc123...

lc2git sync
```

## Automate with cron

Run every night at 23:55 to capture the day's work:

```bash
# crontab -e
55 23 * * * /usr/local/bin/lc2git sync >> ~/.lc2git.log 2>&1
```

## Commands

| Command | Description |
|---------|-------------|
| `lc2git configure` | Interactive credential setup |
| `lc2git sync` | Fetch & push today's solutions |
| `lc2git sync --dry-run` | Fetch only, no push |
| `lc2git show-config` | Print config (tokens masked) |

## How LeetCode Auth Works

LeetCode's API uses two cookies for authentication:
- **LEETCODE_SESSION** — your main session token
- **csrftoken** — required for POST/GraphQL requests

These expire periodically (usually every 30–90 days). Re-run `lc2git configure` when they do.

## License

MIT
