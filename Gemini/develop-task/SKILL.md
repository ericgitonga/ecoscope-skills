---
name: develop-task
description: Develop a new ecoscope workflow task. Use when creating or modifying tasks in ext-ecoscope or ext-custom libraries.
argument-hint: [task-name]
disable-model-invocation: true
---

# Develop Ecoscope Task

> **Environment**: Always use `condpg` to activate the Python environment. Never use `source activate` or `conda activate`.

## Step 1: Gather Requirements

First, ask the user:
1. **New or existing?**: Are you creating a new task or improving an existing one?

### If improving an existing task:
- **Which task?**: Get the task name
- **What change?**: What improvement or fix is needed?
- Use `/home/gitonga/Develop/PGAFF/repos/ecoscope-skills/scripts/search-tasks.py -s <task_name>` to view current implementation
- Skip to Step 3 (location is already known)

### If creating a new task:
- **Purpose**: What should this task do?
- **Where?**: Per-workflow `my-tasks` package (uses `@register`) OR shared `ext-custom` library (uses `@task`)?
- **Task type**: io, transformation, analysis, visualization, config?
- **Inputs**: What parameters does it need? Types?
- **Output**: What does it return? DataFrame, GeoDataFrame, string, list?

## Step 2: Find Location & Similar Tasks (new tasks only)

Search for similar tasks to understand patterns:

```bash
# Search by keyword
/home/gitonga/Develop/PGAFF/repos/ecoscope-skills/scripts/search-tasks.py <keyword>

# View similar task signature
/home/gitonga/Develop/PGAFF/repos/ecoscope-skills/scripts/search-tasks.py -s <task_name>
```

Determine file location based on task type:

| Type | ext-ecoscope path | ext-custom path |
|------|-------------------|-----------------|
| io | `tasks/io/` | `tasks/io/` |
| transformation | `tasks/transformation/` | `tasks/transformation/` |
| analysis | `tasks/analysis/` | `tasks/analysis/` |
| visualization | `tasks/results/` | `tasks/results/` |
| config | `tasks/config/` | `tasks/config/` |

**Library paths:**
- ext-ecoscope: `/home/gitonga/Develop/PGAFF/repos/ecoscope-workflows/src/ecoscope-workflows-ext-ecoscope/ecoscope_workflows_ext_ecoscope/tasks/`
- ext-custom: `/home/gitonga/Develop/PGAFF/repos/ecoscope-workflow-task-library/src/ecoscope-workflows-ext-custom/ecoscope_workflows_ext_custom/tasks/`
- ecoscope (base library): `/home/gitonga/Develop/PGAFF/repos/ecoscope/` - some tasks depend on this library and changes may be needed here

## Step 3: Implement Task

Read `/home/gitonga/Develop/PGAFF/repos/ecoscope-skills/references/ecoscope-tasks.md` for implementation patterns.

1. **Create or edit task file** in the appropriate location
2. **Follow the task template**:

   **Per-workflow task** (`my-tasks` package, `@register`):
   ```python
   from typing import Annotated, cast
   from pydantic import Field
   from wt_registry import register

   @register(title="My Task", description="Brief description of what this task does.")
   def my_task(
       param: Annotated[str, Field(description="Description here.")],
   ) -> ReturnType:
       # Implementation
       return cast(ReturnType, result)
   ```

   **Shared library task** (`ext-custom`, `@task`):
   ```python
   from typing import Annotated, cast
   from pydantic import Field
   from ecoscope_workflows_core.decorators import task

   @task  # or @task(tags=["io"]) for I/O tasks
   def my_task(
       param: Annotated[str, Field(description="Description here.")],
   ) -> ReturnType:
       """Brief description."""
       return cast(ReturnType, result)
   ```

3. **Add to `__init__.py`** (shared library only):
   ```python
   from ._my_file import my_task

   __all__ =[
       ...,
       "my_task",
   ]
   ```

## Step 4: Write Unit Tests

Create test file in the appropriate tests directory:
- ext-ecoscope: `src/ecoscope-workflows-ext-ecoscope/tests/tasks/`
- ext-custom: `src/ecoscope-workflows-ext-custom/tests/tasks/`

Test file template:
```python
import pandas as pd
import pytest

from <package>.tasks.<type> import my_task


def test_my_task_basic():
    # Arrange
    input_data = pd.DataFrame({"col": [1, 2, 3]})

    # Act
    result = my_task(input_data, param="value")

    # Assert
    assert len(result) == 3
    assert "expected_col" in result.columns


def test_my_task_edge_case():
    # Test empty input, null values, etc.
    pass
```

Run unit tests:
```bash
bash -ic 'cd <library-path> && condpg && pytest tests/tasks/test_my_task.py -v'
```

## Step 5: Test in Workflow

1. **Find or create a workflow** that uses this task:
   - If an existing workflow uses the task, use that
   - Otherwise, use or create a test-bed workflow

2. **Update `test-cases.yaml`** to test the specific task change:
   ```yaml
   base:
     name: Base Test Case
     mock_io: true
     params:
       # Add/update parameters for the task being tested
       my_task_id:
         param: "test_value"
   ```
   Note: the rjsf override in spec.yaml does not affect params in test-cases.yaml

3. **Compile and run**:
   ```bash
   cd /home/gitonga/Develop/PGAFF/repos/wt/<workflow-repo> && wt-compiler compile --spec spec.yaml --pkg-name-prefix=ecoscope-workflows --results-env-var=ECOSCOPE_WORKFLOWS_RESULTS --clobber --update && ./dev/pytest-cli.sh <workflow-name> --case base --local --quiet
   ```

4. **Verify the task output** in the test results.

## Supervision Checkpoints

Ask for approval before:
- Writing or modifying task files
- Modifying `__init__.py` exports
- Writing test files
- Running tests that make external API calls
```
