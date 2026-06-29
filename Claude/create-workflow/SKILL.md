---
name: create-workflow
description: Create a new ecoscope workflow. Use when starting a new workflow project, setting up spec.yaml, or scaffolding workflow files.
argument-hint: [workflow-name]
disable-model-invocation: true
---

# Create New Ecoscope Workflow

## Step 1: Load Context

Read references:
- Syntax: `/home/gitonga/Develop/PGAFF/repos/ecoscope-skills/references/ecoscope-spec.md`
- Patterns: `/home/gitonga/Develop/PGAFF/repos/ecoscope-skills/references/ecoscope-workflow-patterns.md`

## Step 2: Gather Requirements

Ask the user:
1. **Purpose**: What should this workflow do?
2. **Data sources**: EarthRanger, Google Earth Engine, external files?
3. **Data types**: Events, observations, patrols, subjects, satellite data?
4. **Outputs**: Data export (CSV, GeoParquet), maps, charts, reports?
5. **Grouping**: Do you want to group the data or not?
6. **Custom tasks**: Does this workflow need custom Python tasks beyond the standard library?
   - If yes: **Bundled** (shipped inside the workflow repo, no separate package) or **Published** (released to a PyPI/conda channel)?

Use the answer to question 6 to determine the scaffold path below.

---

## Path A — No custom tasks / Published custom tasks

Use the standard wt-compiler scaffold:

### Step 3A: Check Existing Tasks

```bash
/home/gitonga/Develop/PGAFF/repos/ecoscope-skills/scripts/search-tasks.py <keyword>
/home/gitonga/Develop/PGAFF/repos/ecoscope-skills/scripts/search-tasks.py -s <task_name>
```

### Step 4A: Scaffold Workflow

```bash
WORKFLOW_ID=$(echo "$ARGUMENTS" | sed 's/^wt-//' | tr '-' '_')
cd /home/gitonga/Develop/PGAFF/repos/wt && wt-compiler scaffold init --no-interactive \
  --workflow-id "$WORKFLOW_ID" \
  --workflow-name "$ARGUMENTS" \
  --author-name "PGAFF" \
  --output-dir . \
  --requirements '{"name":"ecoscope-platform","version":">=2.11.0,<3","channel":"https://repo.prefix.dev/ecoscope-workflows/"}' \
  --requirements '{"name":"ecoscope-workflows-ext-custom","version":">=0.1.0,<1.0.0","channel":"https://repo.prefix.dev/ecoscope-workflows-custom/"}' \
  && [ -d "$WORKFLOW_ID" ] && mv "$WORKFLOW_ID" "wt-$ARGUMENTS" || true
```

If published custom tasks are needed, add them as an additional `--requirements` entry with their
channel and version.

### Step 5A: Post-scaffold cleanup

The scaffold creates a `dev/` directory — delete it:
```bash
rm -rf /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/dev/
```

Copy CI workflows from `wt-custom-events` (the scaffold does not add these):
```bash
cp /home/gitonga/Develop/PGAFF/repos/wt/wt-custom-events/.github/workflows/ci.yml \
   /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/.github/workflows/ci.yml
cp /home/gitonga/Develop/PGAFF/repos/wt/wt-custom-events/.github/workflows/tag.yml \
   /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/.github/workflows/tag.yml
```

### Step 6A: Compile and verify

```bash
cd /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS && wt-compiler compile --spec spec.yaml --pkg-name-prefix=ecoscope-workflows --results-env-var=ECOSCOPE_WORKFLOWS_RESULTS --clobber
```

After recompile, audit `params.json` for fields with `"default": null` AND `"type": "string"` — patch each to `"anyOf": [{"type": "string"}, {"type": "null"}]` so the UI can send explicit nulls.

```bash
pixi run --manifest-path ecoscope-workflows-$ARGUMENTS-workflow/pixi.toml --locked -e test test-app-sequential-mock-io
```

---

## Path B — Bundled custom tasks

Use `wt/wt-custom-events` as the reference template. Study that repo before proceeding:

```
/home/gitonga/Develop/PGAFF/repos/wt/wt-custom-events/
```

Key characteristics of the bundled pattern:
- The tasks package lives **inside** the compiled workflow package directory:
  `ecoscope-workflows-<name>-workflow/<name>-tasks/`
- `pixi.toml` references it as `path = "./<name>-tasks"` (relative — portable across machines)
- `pixi.lock` must be regenerated with `pixi update` after any path change
- `conftest.py` snapshot dirs point to `~/.config/ecoscope-desktop/data/workflows/<org>-wt-<name>/`
  rather than the repo, so test artifacts stay local
- `spec.yaml` references the tasks package by absolute path (local dev only — does not affect published users)
- `wt-compiler-env-overrides.toml` is **not** used; bundled path is handled via `pixi.toml` directly

### Step 3B: Scaffold base workflow

Run the standard scaffold (same as Path A), then adapt:

```bash
WORKFLOW_ID=$(echo "$ARGUMENTS" | sed 's/^wt-//' | tr '-' '_')
cd /home/gitonga/Develop/PGAFF/repos/wt && wt-compiler scaffold init --no-interactive \
  --workflow-id "$WORKFLOW_ID" \
  --workflow-name "$ARGUMENTS" \
  --author-name "PGAFF" \
  --output-dir . \
  --requirements '{"name":"ecoscope-platform","version":">=2.11.0,<3","channel":"https://repo.prefix.dev/ecoscope-workflows/"}' \
  && [ -d "$WORKFLOW_ID" ] && mv "$WORKFLOW_ID" "wt-$ARGUMENTS" || true
```

Delete the `dev/` directory the scaffold creates (not part of canonical structure):
```bash
rm -rf /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/dev/
```

Copy CI workflows from `wt-custom-events`:
```bash
cp /home/gitonga/Develop/PGAFF/repos/wt/wt-custom-events/.github/workflows/ci.yml \
   /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/.github/workflows/ci.yml
cp /home/gitonga/Develop/PGAFF/repos/wt/wt-custom-events/.github/workflows/tag.yml \
   /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/.github/workflows/tag.yml
```

### Step 4B: Create the tasks package

Inside the compiled workflow package directory, create the tasks package:

```
ecoscope-workflows-<name>-workflow/
  <name>-tasks/
    pyproject.toml
    src/
      <name>_tasks/
        __init__.py
        <task_file>.py
```

`pyproject.toml` must include the `wt_registry` entry point:
```toml
[project]
name = "<name>-tasks"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = []

[project.entry-points."wt_registry"]
<name>_tasks = "<name>_tasks"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/<name>_tasks"]
```

### Step 5B: Wire into pixi.toml

In `ecoscope-workflows-<name>-workflow/pixi.toml`, add the tasks package using a relative path
in **all three** feature sections (default, runner, test):

```toml
[pypi-dependencies.<name>-tasks]
path = "./<name>-tasks"
editable = true

[feature.runner.pypi-dependencies.<name>-tasks]
path = "./<name>-tasks"
editable = true

[feature.test.pypi-dependencies.<name>-tasks]
path = "./<name>-tasks"
editable = true
```

### Step 6B: Update conftest.py snapshot dirs

In `ecoscope-workflows-<name>-workflow/tests/conftest.py`, redirect snapshot output away from the repo:

```python
_WORKFLOW_DATA_DIR = (
    Path.home()
    / ".config"
    / "ecoscope-desktop"
    / "data"
    / "workflows"
    / "<org>-wt-<name>"
)
SNAPSHOT_DIRNAME = _WORKFLOW_DATA_DIR / "__results_snapshots__"
SNAPSHOT_DIFF_OUTPUT_DIRNAME = _WORKFLOW_DATA_DIR / "__diff_output__"
```

Add both dirs to `.gitignore`:
```
__results_snapshots__/
__diff_output__/
```

### Step 7B: Update spec.yaml

Add the tasks package requirement (absolute path for local dev):
```yaml
requirements:
  - name: ecoscope-platform
    version: ">=2.16.0,<2.17.0"
    channel: https://repo.prefix.dev/ecoscope-workflows/
  - name: <name>-tasks
    path: /home/gitonga/Develop/PGAFF/repos/wt/wt-<name>/ecoscope-workflows-<name>-workflow/<name>-tasks
    editable: true
```

### Step 8B: Regenerate pixi.lock

After wiring the paths:
```bash
cd /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/ecoscope-workflows-<name>-workflow && pixi update
```

Verify no absolute paths leaked into the lock file:
```bash
grep "/home/" pixi.lock  # should return nothing
```

### Step 9B: Audit params.json for nullable fields

After compile, check for fields with `"default": null` AND `"type": "string"` in `params.json` — these reject explicit nulls from the UI. Patch each to `"anyOf": [{"type": "string"}, {"type": "null"}]`.

### Step 10B: Verify

```bash
pixi run --manifest-path /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/ecoscope-workflows-<name>-workflow/pixi.toml --locked -e test test-app-sequential-mock-io
```

---

## Supervision Checkpoints

Ask for approval before:
- Writing any files
- Suggesting new tasks that need implementation
- Making changes to task libraries
