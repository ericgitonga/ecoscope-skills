---
name: publish-workflow
description: Publish workflow changes by updating dependencies and creating a PR.
argument-hint: [repo-name]
---

# Publish Workflow Skill

Publish workflow changes by updating dependencies and creating a PR.

## Usage

```
/publish-workflow <repo-name>
```

- Target repo: `/home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS` (If `$ARGUMENTS` does not include the `wt-` prefix, add it).
- Example: `/publish-workflow patrol-events`

## Workflow

### 0. Ask where to publish

Before doing anything else, ask the user three questions:

> 1. Where would you like to publish this workflow?
>    - **github.com/ericgitonga** — personal/testing repository
>    - **github.com/wildlife-dynamics** — official Wildlife Dynamics organisation
>
> 2. What should the branch be named? It will be prefixed with `er/` — e.g. enter `update-workflow` to get `er/update-workflow`.
>
> 3. What version should this workflow be bumped to?
>    Check the current version first:
>    ```bash
>    find /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS -name "VERSION.yaml" | xargs grep -H .
>    ```
>    Common choices: patch bump (0.0.1 → 0.0.2), minor bump (0.0.0 → 0.1.0), or keep as-is.

Wait for all three answers before proceeding. Use:
- The chosen GitHub organisation as `$ORG`
- The full branch name as `er/$BRANCH_NAME`
- The target version decomposed as `$MAJ`, `$MIN`, `$PATCH` (e.g. "0.1.0" → MAJ=0, MIN=1, PATCH=0)

### 1. Create and switch to branch

```bash
git checkout -b er/$BRANCH_NAME
```

Never make changes directly on `main` or `master`.

### 2. Check for uncommitted changes

```bash
git status --porcelain
```
If there are uncommitted changes on the branch, ask the user if they want to commit them first.

### 3. Update task libraries to latest main

```bash
# ecoscope-workflows (compiler + core tasks)
cd /home/gitonga/Develop/PGAFF/repos/ecoscope-workflows && git checkout main && git pull

# ecoscope-workflow-task-library (custom tasks)
cd /home/gitonga/Develop/PGAFF/repos/ecoscope-workflow-task-library && git checkout main && git pull
```

### 4. Get latest versions

Check the latest version by git tag:
```bash
git describe --tags --abbrev=0
```

### 5. Update versions

Update `spec.yaml` requirements section (wt-compiler reads these to manage its compilation environment):
```yaml
requirements:
  - name: ecoscope-workflows-core
    version: ">=X.Y.Z, <X.Y+1.0"
  - name: ecoscope-workflows-ext-ecoscope
    version: ">=X.Y.Z, <X.Y+1.0"
  - name: ecoscope-workflows-ext-custom
    version: ">=X.Y.Z, <X.Y+1.0"
```

### 6. Recompile workflow and bump version

```bash
cd /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS && wt-compiler compile --spec spec.yaml --pkg-name-prefix=ecoscope-workflows --results-env-var=ECOSCOPE_WORKFLOWS_RESULTS --clobber --update
```

After compilation, bump the version in every `VERSION.yaml` found in compiled workflow package directories:

```bash
# Find and update all VERSION.yaml files (wt-compiler resets them to 0.0.0 on --clobber)
find /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS -name "VERSION.yaml" -exec \
  sh -c 'echo "{MAJ: $MAJ, MIN: $MIN, PATCH: $PATCH}" > "$1"' _ {} \;
```

Verify the files were updated, then update the version in `README.md`:

```bash
# Update the version badge line in README.md (matches "**Version X.Y.Z**")
sed -i "s/\*\*Version [0-9]\+\.[0-9]\+\.[0-9]\+\*\*/**Version $MAJ.$MIN.$PATCH**/" \
  /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/README.md
```

Confirm the README line now reads `**Version $MAJ.$MIN.$PATCH**`, then commit:

```bash
git add -A && git commit -m "chore: bump version to $MAJ.$MIN.$PATCH and recompile"
```

### 7. Update and test in ecoscope-workflows

```bash
bash -ic 'cd /home/gitonga/Develop/PGAFF/repos/ecoscope-workflows && pixi update && pixi run bash -c "./dev/pytest-cli.sh $ARGUMENTS --all --quiet"'
```

### 8. Create GitHub repo (first publish only)

If the repo does not yet exist on GitHub:

```bash
# Create repo under chosen org
conda run -n pgaff gh repo create $ORG/wt-$ARGUMENTS --public --description "<short description>"

# Set SSH remote
git remote add origin git@github.com:$ORG/wt-$ARGUMENTS.git

# Push main first (empty or existing base), then the branch
git push -u origin main
```

### 9. Push branch and open PR

```bash
# Push the branch
git push -u origin er/$BRANCH_NAME

# Open a PR — do NOT merge, the user will do that manually after testing
conda run -n pgaff gh pr create \
  --repo $ORG/wt-$ARGUMENTS \
  --base main \
  --head er/$BRANCH_NAME \
  --title "<descriptive title>" \
  --body "$(cat <<'EOF'
## Summary
- <bullet points describing changes>

## Test plan
- [ ] Mock-io tests pass
- [ ] Workflow runs in ecoscope-desktop against target data source

> Merge manually after testing is complete.
EOF
)"
```

Return the PR URL to the user. **Stop here.** The user merges manually after testing.

### 10. Tag, release, and update local — wait for user go-ahead

After returning the PR URL, **do not proceed further**. Wait for the user to confirm the PR has been merged, then ask:

> The PR is merged — shall I tag `v$MAJ.$MIN.$PATCH`, create the GitHub Release, and update your local repo?

Only proceed when they say yes. Then run:

```bash
git checkout main && git pull origin main

# Create annotated tag
git tag v$MAJ.$MIN.$PATCH
git push origin v$MAJ.$MIN.$PATCH

# Create GitHub Release from the tag (this is what shows in the Releases panel)
conda run -n pgaff gh release create v$MAJ.$MIN.$PATCH \
  --repo $ORG/wt-$ARGUMENTS \
  --title "v$MAJ.$MIN.$PATCH" \
  --generate-notes
```

Confirm the release is visible at `https://github.com/$ORG/wt-$ARGUMENTS/releases`, then tell the user the local repo is up to date.

## Technical Guide

If this workflow does not yet have a `docs/technical_guide.pdf`, generate one before
pushing the PR. Use the `generate-tech-guide` skill:

```
/generate-tech-guide $ARGUMENTS
```

Or run the steps manually — see `Gemini/generate-tech-guide/SKILL.md` for the full
procedure. Key points:

- Use **ReportLab** via `conda run -n ds python docs/generate_technical_guide.py`
- Never use weasyprint
- The script lives at `docs/generate_technical_guide.py` alongside the PDF
- README must link to `docs/technical_guide.pdf`

If a guide already exists and the workflow logic has not changed, skip this step.
If workflow logic changed (new tasks, new outputs), regenerate the PDF and commit
the updated script and PDF in the same PR.

## Notes
- Version format: `>=X.Y.Z, <X.Y+1.0` (semver compatible range)
- Always verify the workflow compiles successfully before pushing
- Check for breaking changes in task library updates
- Branch prefix is always `er/` — never push changes directly to `main`
- If a release already exists for a tag (e.g. created by GitHub on merge), skip `gh release create`
  and verify with `conda run -n pgaff gh release list --repo $ORG/wt-$ARGUMENTS`
