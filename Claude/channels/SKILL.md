---
name: channels
description: Switch task library channels between local and release modes across workflow and task library repos.
argument-hint: <mode> [repo-name]
---

# Channels Skill

> **Instructions for Claude**: Use your `Replace` or `Edit` file tools to make these modifications directly to the files. Ensure you preserve surrounding yaml/toml structures and comments.

Switch task library channels between local and release modes across workflow and task library repos.

## Usage

```
/channels <mode> [repo-name]
```

## Arguments
The user will pass arguments which are available as `$ARGUMENTS`.
Parse `$ARGUMENTS` to determine:
1. `<mode>`: `local`, `release`, or `status`
2. `[repo-name]`: Workflow repo name (e.g., `download-events`). If omitted, ask the user.

## Repo Paths

- Workflows: `/home/gitonga/Develop/PGAFF/repos/wt/wt-<repo-name>/`
- Task library: `/home/gitonga/Develop/PGAFF/repos/ecoscope-workflow-task-library/src/ecoscope-workflows-ext-custom/`
- Compiler repo: `/home/gitonga/Develop/PGAFF/repos/ecoscope-workflows/`

## Channel URL Mapping

| Package | Local Channel | Release Channel (wt-* repos) | Release Channel (task lib pyproject.toml) |
|---|---|---|---|
| ecoscope-workflows-core | `file:///tmp/ecoscope-workflows/release/artifacts/` | `https://repo.prefix.dev/ecoscope-workflows/` | `https://prefix.dev/ecoscope-workflows` |
| ecoscope-workflows-ext-ecoscope | `file:///tmp/ecoscope-workflows/release/artifacts/` | `https://repo.prefix.dev/ecoscope-workflows/` | `https://prefix.dev/ecoscope-workflows` |
| ecoscope-workflows-ext-custom | `file:///tmp/ecoscope-workflows-custom/release/artifacts/` | `https://repo.prefix.dev/ecoscope-workflows-custom/` | `https://prefix.dev/ecoscope-workflows-custom` |

Note: wt-* repos use `repo.prefix.dev` while the task library pyproject.toml uses `prefix.dev` (no `repo.` subdomain).

Note: `wt-compiler` reads channels and requirements directly from `spec.yaml` to manage its own ephemeral compilation environment — no separate `[feature.compile.dependencies]` in pixi.toml is needed.

## Workflow

### `/channels status [repo-name]`

1. Read `wt-*/spec.yaml` and `ext-custom/pyproject.toml`
2. Check which channel URLs are present (local vs release)
3. Report the mode of each file

### `/channels local [repo-name]`

#### Step 1: Identify workflow repo
Ask which `wt-*` repo if not specified.

#### Step 2: Get latest versions from main
```bash
cd /home/gitonga/Develop/PGAFF/repos/ecoscope-workflows && git checkout main && git pull && git describe --tags --abbrev=0
cd /home/gitonga/Develop/PGAFF/repos/ecoscope-workflow-task-library && git checkout main && git pull && git describe --tags --abbrev=0
```
Record these versions for reference (shown to user), but local mode uses `"*"` for all versions.

#### Step 3: Edit `wt-*/spec.yaml`
Change each requirement's channel to its local equivalent, and set version to `"*"`:
```yaml
# FROM (release):
requirements:
  - name: ecoscope-workflows-core
    version: ">=0.22.12, <0.23.0"
    channel: https://repo.prefix.dev/ecoscope-workflows/
  - name: ecoscope-workflows-ext-ecoscope
    version: ">=0.22.12, <0.23.0"
    channel: https://repo.prefix.dev/ecoscope-workflows/
  - name: ecoscope-workflows-ext-custom
    version: ">=0.0.28, <0.1.0"
    channel: https://repo.prefix.dev/ecoscope-workflows-custom/

# TO (local):
requirements:
  - name: ecoscope-workflows-core
    version: "*"
    channel: file:///tmp/ecoscope-workflows/release/artifacts/
  - name: ecoscope-workflows-ext-ecoscope
    version: "*"
    channel: file:///tmp/ecoscope-workflows/release/artifacts/
  - name: ecoscope-workflows-ext-custom
    version: "*"
    channel: file:///tmp/ecoscope-workflows-custom/release/artifacts/
```

#### Step 4: Edit `ext-custom/pyproject.toml`

**Channels array**: Ensure local channel is first entry:
```toml
# Ensure this is present as first channel:
[tool.pixi.workspace]
channels =[
    "file:///tmp/ecoscope-workflows/release/artifacts/",
    "https://prefix.dev/ecoscope-workflows-custom",
    "https://prefix.dev/ecoscope-workflows",
    "conda-forge",
]
```

**Dependencies**: Use channel override (no version pin):
```toml
# FROM (release):
ecoscope-workflows-core = ">=0.22.12, <1.0.0"
ecoscope-workflows-ext-ecoscope = ">=0.22.12, <1.0.0"

# TO (local):
ecoscope-workflows-core = { channel = "file:///tmp/ecoscope-workflows/release/artifacts/" }
ecoscope-workflows-ext-ecoscope = { channel = "file:///tmp/ecoscope-workflows/release/artifacts/" }
```

#### Step 5: Clean up ext-custom pixi environment
```bash
rm -rf /home/gitonga/Develop/PGAFF/repos/ecoscope-workflow-task-library/src/ecoscope-workflows-ext-custom/.pixi
rm -f /home/gitonga/Develop/PGAFF/repos/ecoscope-workflow-task-library/src/ecoscope-workflows-ext-custom/pixi.lock
```

#### Step 6: Optionally build conda packages
Ask user: "Build conda packages?" If yes:
```bash
cd /home/gitonga/Develop/PGAFF/repos/ecoscope-workflows && ./publish/build.sh release
cd /home/gitonga/Develop/PGAFF/repos/ecoscope-workflow-task-library && ./publish/build.sh
```

#### Step 7: Optionally recompile
Ask user: "Recompile workflow?" If yes:
```bash
cd /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS && wt-compiler compile --spec spec.yaml --pkg-name-prefix=ecoscope-workflows --results-env-var=ECOSCOPE_WORKFLOWS_RESULTS --clobber --update
```

---

### `/channels release [repo-name]`

#### Step 1: Identify workflow repo
Ask which `wt-*` repo if not specified.

#### Step 2: Get latest versions from main
```bash
cd /home/gitonga/Develop/PGAFF/repos/ecoscope-workflows && git checkout main && git pull && git describe --tags --abbrev=0
cd /home/gitonga/Develop/PGAFF/repos/ecoscope-workflow-task-library && git checkout main && git pull && git describe --tags --abbrev=0
```

#### Step 3: Compute version constraints
- For `ecoscope-workflows` tag (e.g. `v0.22.12`): extract `0.22.12`, compute constraint `">=0.22.12, <0.23.0"`
- For `ecoscope-workflow-task-library` tag (e.g. `v0.0.28`): extract `0.0.28`, compute constraint `">=0.0.28, <0.1.0"`
- Version constraint format: `>=X.Y.Z, <X.Y+1.0` (bump minor, reset patch to 0)
- Show computed versions to user for confirmation before editing files.

#### Step 4: Edit `wt-*/spec.yaml`
Change each requirement's channel to release, update version constraints:
```yaml
requirements:
  - name: ecoscope-workflows-core
    version: ">=0.22.12, <0.23.0"
    channel: https://repo.prefix.dev/ecoscope-workflows/
  - name: ecoscope-workflows-ext-ecoscope
    version: ">=0.22.12, <0.23.0"
    channel: https://repo.prefix.dev/ecoscope-workflows/
  - name: ecoscope-workflows-ext-custom
    version: ">=0.0.28, <0.1.0"
    channel: https://repo.prefix.dev/ecoscope-workflows-custom/
```

#### Step 5: Edit `ext-custom/pyproject.toml`

**Channels array**: Remove local channel:
```toml
[tool.pixi.workspace]
channels =[
    "https://prefix.dev/ecoscope-workflows-custom",
    "https://prefix.dev/ecoscope-workflows",
    "conda-forge",
]
```

**Dependencies**: Use version-pinned format (no channel override):
```toml
ecoscope-workflows-core = ">=0.22.12, <1.0.0"
ecoscope-workflows-ext-ecoscope = ">=0.22.12, <1.0.0"
```

#### Step 6: Optionally recompile
Ask user: "Recompile workflow?" If yes:
```bash
cd /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS && wt-compiler compile --spec spec.yaml --pkg-name-prefix=ecoscope-workflows --results-env-var=ECOSCOPE_WORKFLOWS_RESULTS --clobber --update
```

## Important Notes

- Always show a summary of changes before making edits
- Always show a summary of changes after making edits
- Preserve comments and formatting in files where possible
- The `ext-custom/pyproject.toml` commented-out lines (lines 75-76) serve as documentation of the release format — preserve them
- Do NOT modify the `ecoscope-workflows` repo itself
- wt-compiler manages its own ephemeral environment from spec.yaml — no pixi.toml compile feature changes are needed in wt-* repos
