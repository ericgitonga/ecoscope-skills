---
name: develop-workflow
description: Improve an existing ecoscope workflow. Use when adding features, fixing bugs, or updating configuration.
argument-hint:[workflow-name]
disable-model-invocation: true
---

# Develop Workflow: wt-$ARGUMENTS

> **Instructions for Claude**: Use your `Replace` or `Edit` file tools to make these modifications directly to the files. Ensure you preserve surrounding yaml/toml structures and comments.

Workflow directory: `/home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/`

## Checklist

### 1. Gather Requirements
Ask user:
- What improvement is needed? (feature, bug fix, UI update, performance)

Read current state:
```bash
cat /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/spec.yaml
cat /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/test-cases.yaml
```

### 2. Find/Create Tasks
Search for existing tasks:
```bash
/home/gitonga/Develop/PGAFF/repos/ecoscope-skills/scripts/search-tasks.py <keyword>
/home/gitonga/Develop/PGAFF/repos/ecoscope-skills/scripts/search-tasks.py -s <task_name>
```

- **Task exists**: Proceed to step 3
- **Task needs changes**: → Invoke the `develop-task` tool with `<task_name>`, then resume
- **New task needed**: → Invoke the `develop-task` tool, then resume

### 3. Update spec.yaml
Reference:
- Syntax: `/home/gitonga/Develop/PGAFF/repos/ecoscope-skills/references/ecoscope-spec.md`
- Patterns: `/home/gitonga/Develop/PGAFF/repos/ecoscope-skills/references/ecoscope-workflow-patterns.md`

After changes, compile:
```bash
cd /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS && wt-compiler compile --spec spec.yaml --pkg-name-prefix=ecoscope-workflows --results-env-var=ECOSCOPE_WORKFLOWS_RESULTS --clobber --update
```

### 4. Update test-cases.yaml
Add/modify test parameters for new functionality. Run tests:
```bash
cd /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS && ./dev/pytest-cli.sh $ARGUMENTS --case <case-name> --local --quiet
```
Note: the rjsf override in spec.yaml does not affect params in test-cases.yaml

### 5. Validate Form
→ Invoke the `validate-rjsf` tool with `$ARGUMENTS`

### 6. Update Layout (if dashboard changed)
→ Invoke the `edit-layout` tool with `$ARGUMENTS`

### 7. Update Templates (if docx output changed)
User updates `resources/templates/*.docx` manually. Wait for confirmation.

### 8. Update README
→ Invoke the `ecoscope-user-guide` tool for `$ARGUMENTS`

### 9. Final Verification
```bash
cd /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS && ./dev/pytest-cli.sh $ARGUMENTS --all --local --quiet && git status && git diff
```

Summarize changes for user.

### 10. Publish
→ Invoke the `publish-workflow` tool with `$ARGUMENTS`

## Supervision Checkpoints

Ask for approval before:
- Modifying spec.yaml, test-cases.yaml, layout.json, README.md
- Running tests with `mock_io: false`
- Any git operations
