---
name: validate-rjsf
description: Validate and customize workflow configuration form (rjsf.json). Use after compiling a workflow to check form rendering.
argument-hint: [workflow-name]
disable-model-invocation: true
---

# Validate Configuration Form

Validate the compiled workflow's form schema for workflow `wt-$ARGUMENTS`.

## Step 1: Find rjsf.json

```bash
cat /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/ecoscope-workflows-$ARGUMENTS-workflow/ecoscope_workflows_$ARGUMENTS_workflow/rjsf.json
```
And highlight the differences from the latest git commit.

## Step 2: User Validation

Tell user to validate in browser:
1. Open https://app.dev.ecoscope.io/configuration-form-playground
2. Copy/paste the rjsf.json content
3. Check form renders correctly
4. Verify field labels, descriptions, defaults

## Step 3: Gather Feedback

Ask user:
- Do field labels make sense?
- Are descriptions helpful?
- Are defaults appropriate?
- Any fields need reordering or hiding?

## Step 4: Apply Adjustments

If adjustments needed, update `rjsf-overrides` in spec.yaml:

```yaml
rjsf-overrides:
  properties:
    task_id.properties.param_name.default: "value"
    task_id.properties.param_name.description: "Help text"
    task_id.properties.param_name.title: "Display Title"
  uiSchema:
    task_id.param_name.ui:options.label: false
```

## Step 5: Recompile

After any changes:
```bash
cd /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS && wt-compiler compile --spec spec.yaml --pkg-name-prefix=ecoscope-workflows --results-env-var=ECOSCOPE_WORKFLOWS_RESULTS --clobber --update
```

Repeat Steps 1-5 until user is satisfied.

## Supervision Checkpoints

Ask for approval before:
- Modifying spec.yaml rjsf-overrides
