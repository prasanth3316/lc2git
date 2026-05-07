# lc2git Usage

`lc2git` syncs your accepted LeetCode submissions to a GitHub repository.

## Install

```bash
pip install lc2git
```

## 1) Configure credentials

Run interactive setup:

```bash
lc2git configure
```

You will be asked for:

- `GITHUB_TOKEN` (GitHub personal access token with repo write access)
- `GITHUB_REPO` (example: `username/leetcode-solutions`)
- `GITHUB_BRANCH` (usually `main`)
- `LEETCODE_SESSION` cookie
- `csrftoken` cookie

## 2) Sync solutions

```bash
lc2git sync
```

Preview without pushing:

```bash
lc2git sync --dry-run
```

Show current saved config (masked):

```bash
lc2git show-config
```

---

## Environment Variable Mode (CI-friendly)

You can skip prompts and configure from environment variables:

```bash
export GITHUB_TOKEN="ghp_..."
export GITHUB_REPO="username/leetcode-solutions"
export GITHUB_BRANCH="main"
export LEETCODE_SESSION="eyJ..."
export LEETCODE_CSRF_TOKEN="..."

lc2git sync
```

---

## How to get required tokens/cookies

### GitHub token
1. Go to GitHub → Settings → Developer settings → Personal access tokens.
2. Create a token with repository write access (`repo` scope for classic tokens).
3. Copy and store it securely.

### LeetCode cookies
1. Log in to `https://leetcode.com`.
2. Open browser DevTools.
3. Go to Application/Storage → Cookies → `leetcode.com`.
4. Copy:
   - `LEETCODE_SESSION`
   - `csrftoken` (set this as `LEETCODE_CSRF_TOKEN`)

---

## Notes

- LeetCode cookies expire periodically. Reconfigure when sync starts failing with auth errors.
- Keep tokens private and rotate if exposed.
- Target GitHub repository must already exist.
