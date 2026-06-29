---
name: pr
description: Create or update a GitHub pull request with linked issue.
---

# PR Skill

Create or update a GitHub pull request with linked issue.

If the user passes `$ARGUMENTS`, use them to determine the `<description>` or `<title>` of the PR and Issue.

## GitHub CLI

All `gh` commands must use the SSH-authenticated binary directly:
```bash
GH=/home/gitonga/miniforge3/envs/pgaff/bin/gh
```

## Workflow

### 1. Check for existing PR
```bash
GH=/home/gitonga/miniforge3/envs/pgaff/bin/gh
$GH pr view --json number,url 2>/dev/null
```

### 2. Commit changes on current branch
If there are uncommitted changes:
```bash
git add -A && git commit -m "<type>: <description>"
```

> **Important**: Never commit directly to main. If on main, create a new branch first.

### 3. Rebase on latest main
```bash
git fetch origin main && git rebase origin/main
```

### 4. If PR exists and not closed
Pull latest and rebase, then push updates:
```bash
git pull --rebase && git push
```

### 5. If no open PR exists

Create issue:
```bash
GH=/home/gitonga/miniforge3/envs/pgaff/bin/gh
$GH issue create --title "<type>: <description>" --body "<details>" --assignee @me
```

Push branch:
```bash
git push -u origin $(git branch --show-current)
```

Create PR referencing issue:
```bash
GH=/home/gitonga/miniforge3/envs/pgaff/bin/gh
$GH pr create --title "<title>" --body "## Summary
- Change 1
- Change 2

Closes #<issue-number>

🤖 Generated with Claude Code"
```

## Notes
- Issue title format: `feat:`, `fix:`, `docs:`, `refactor:`
- Always include `Closes #<issue>` to auto-close on merge
