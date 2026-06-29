# spec.yaml Reference

Single source of truth for workflow spec.yaml structure and syntax.

---

## Full Structure

```yaml
id: workflow_name                    # Valid Python identifier, max 64 chars

# New unified format (ecoscope-platform >= 2.11)
requirements:
  - name: ecoscope-platform
    version: ">=2.11.0, <3"
    channel: https://repo.prefix.dev/ecoscope-workflows/
  - name: ecoscope-workflows-ext-custom      # Optional: PGAFF shared task library
    version: ">=0.1.0, <1.0.0"
    channel: https://repo.prefix.dev/ecoscope-workflows-custom/
  - name: my-tasks                           # Optional: local dev task package
    path: /absolute/path/to/my-tasks
    editable: true

# Legacy format (ecoscope-workflows-core + ext-ecoscope)
requirements:
  - name: ecoscope-workflows-core
    version: ">=0.22.0, <0.23.0"
    channel: https://repo.prefix.dev/ecoscope-workflows/
  - name: ecoscope-workflows-ext-ecoscope
    version: ">=0.22.0, <0.23.0"
    channel: https://repo.prefix.dev/ecoscope-workflows/
  - name: ecoscope-workflows-ext-custom      # Optional
    version: ">=0.0.26, <0.1.0"
    channel: https://repo.prefix.dev/ecoscope-workflows-custom/

rjsf-overrides:                      # React JSON Schema Form UI customizations
  $defs:
    ValueGrouper.oneOf: [{"const": "col", "title": "Display"}]
  properties:
    task_id.properties.arg.default: "value"
    task_id.properties.arg.description: "Help text"
    task_id.properties.arg.title: "Display Title"
  uiSchema:
    task_id.arg.ui:options.label: false

task-instance-defaults:              # Applied to all tasks unless overridden
  skipif:
    conditions:
      - any_is_empty_df
      - any_dependency_skipped

workflow:                            # List of task instances and/or task groups
  - name: "Human Readable Name"
    id: task_id                      # Python identifier, max 32 chars, unique
    task: known_task_name            # From registry
    partial:                         # Static kwargs
      arg: "literal_value"
      dep: ${{ workflow.other_task.return }}
      env_var: ${{ env.VAR_NAME }}
    map:                             # Parallel over iterable
      argnames: arg_name
      argvalues: ${{ workflow.iterable_task.return }}
    mapvalues:                       # Parallel key-value (preserves keys)
      argnames: arg_name
      argvalues: ${{ workflow.dict_task.return }}
    skipif:
      conditions:
        - any_is_empty_df
```

---

## Variable Reference Syntax

| Syntax | Description | Example |
|--------|-------------|---------|
| `${{ workflow.<id>.return }}` | Reference task output | `${{ workflow.get_data.return }}` |
| `${{ env.<VAR> }}` | Environment variable | `${{ env.ECOSCOPE_WORKFLOWS_RESULTS }}` |
| Inline literals | Strings, numbers, bools, null, lists, dicts | `"value"`, `42`, `true` |

---

## Task Instance Methods

| Method | Description | Config |
|--------|-------------|--------|
| `call` | Single invocation (default) | No map/mapvalues |
| `map` | Parallel over iterable | `map: { argnames: x, argvalues: ${{ ... }} }` |
| `mapvalues` | Parallel key-value pairs | `mapvalues: { argnames: x, argvalues: ${{ ... }} }` |

Only one of `map` or `mapvalues` can be specified per task.

---

## Task Groups

Group related tasks for UI organization:

```yaml
- title: "Process Data"
  type: task-group
  description: "Data processing steps"
  tasks:
    - name: "Filter"
      id: filter_data
      task: apply_filter
      partial:
        df: ${{ workflow.input.return }}
```

---

## skipif Conditions

| Condition | Description |
|-----------|-------------|
| `any_is_empty_df` | Skip if any input DataFrame is empty |
| `any_dependency_skipped` | Skip if any upstream task was skipped |
| `all_geometry_are_none` | Skip if no valid geometries |
| `never` | Never skip (always run) |

---

## Validation Rules

1. **Spec ID**: Valid Python identifier, max 64 chars, not a keyword/builtin
2. **Task IDs**: Valid Python identifier, max 32 chars, unique
3. **Task IDs cannot match task names**: Use different id than the task name
4. **Dependencies**: Must reference existing task IDs
5. **Topological Order**: Tasks must be defined before dependents
6. **Mutual Exclusion**: Cannot use both `map` and `mapvalues` on same task

### Task ID Naming Constraint

```yaml
# WRONG - id matches task name
- id: add_temporal_index
  task: add_temporal_index

# CORRECT - use different id
- id: temporal_index
  task: add_temporal_index
```

---

## rjsf-overrides Paths

```yaml
rjsf-overrides:
  properties:
    # Direct task path
    task_id.properties.param_name.default: "value"

    # Task group path (use quotes for dots in group title)
    "Group Title.properties.task_id.properties.param_name.default": "value"

  uiSchema:
    # Hide labels for array items
    task_id.param_name.items.ui:options.label: false
```
