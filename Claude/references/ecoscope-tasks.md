# Ecoscope Task Development

Reference for implementing workflow tasks.

---

## Decorator Usage

Two patterns exist depending on where the task lives:

### Per-Workflow Tasks (my-tasks / wt_registry — preferred for new tasks)
```python
from wt_registry import register

@register(title="Simple Task", description="Brief description of what this task does.")
def simple_task(param: str) -> str:
    return param

@register(title="Fetch Data", description="Fetches data from EarthRanger.")
def fetch_data(client: EarthRangerClient, time_range: TimeRange) -> DataFrame:
    ...
```

### Shared Library Tasks (ext-custom — ecoscope_workflows entry point)
```python
from ecoscope_workflows_core.decorators import task

@task
def simple_task(param: str) -> str:
    return param

@task(tags=["io"])
def fetch_data(client: Client, time_range: TimeRange) -> DataFrame:
    ...
```

---

## Parameter Annotations

### Basic Field
```python
param: Annotated[str, Field(description="What this parameter does.")]
```

### Field with Default
```python
param: Annotated[str, Field(description="...")] = "default_value"
```

### AdvancedField (hidden in basic UI)
```python
from ecoscope_workflows_core.annotations import AdvancedField

param: Annotated[bool, AdvancedField(
    default=True,
    title="Display Title",
    description="Detailed description."
)] = True
```

### Union Types
```python
param: Annotated[str | None, Field(description="Optional.")] = None
param: Annotated[list[str] | None, Field(description="Optional list.")] = None
```

### Literal for Enum-like Choices
```python
how: Annotated[
    Literal["left", "right", "inner", "outer"],
    Field(description="Join type.")
] = "inner"
```

---

## Return Type Patterns

```python
# Simple
def task_name(...) -> str:
def task_name(...) -> pd.DataFrame:

# Union (for empty data handling)
def task_name(...) -> DataFrame | EmptyDataFrame:
def task_name(...) -> GeoDataFrame | None:

# Annotated (for UI metadata)
def task_name(...) -> Annotated[list[str], Field(description="...")]:

# Schema-Validated DataFrame
from pandera.typing import DataFrame
def task_name(...) -> DataFrame[MySchema]:
```

---

## Common Type Aliases

From `ecoscope_workflows_core.annotations`:
```python
AnyDataFrame          # pd.DataFrame | gpd.GeoDataFrame
TimeRange             # Pydantic model for time ranges
```

From `ecoscope_workflows_ext_ecoscope.annotations`:
```python
EarthRangerClient
TrajectoryGDF, SubjectGroupObservationsGDF, EventsGDF, PatrolsGDF
EmptyDataFrame        # Marker for empty results
```

---

## Type Casting

Always cast return values for type checker:
```python
from typing import cast

def my_task(df: AnyDataFrame) -> AnyDataFrame:
    result = df.copy()
    return cast(AnyDataFrame, result)
```

---

## Common Imports

```python
from typing import Annotated, Literal, cast
import pandas as pd
import geopandas as gpd
from pydantic import Field

from ecoscope_workflows_core.decorators import task
from ecoscope_workflows_core.annotations import AnyDataFrame, AdvancedField

# For ext-ecoscope tasks
from ecoscope_workflows_ext_ecoscope.annotations import (
    EarthRangerClient, TimeRange, EmptyDataFrame,
)
```

---

## File Structure

### Per-Workflow Task File (`my_task.py`)
```python
"""Module docstring."""

from typing import Annotated, cast
import pandas as pd
from pydantic import Field
from wt_registry import register
from ecoscope_workflows_core.annotations import AnyDataFrame


@register(title="My Task", description="Process the DataFrame.")
def my_task(
    df: Annotated[AnyDataFrame, Field(description="Input DataFrame.")],
) -> AnyDataFrame:
    result = df.copy()
    return cast(AnyDataFrame, result)
```

### Shared Library Task File (`_my_task.py`)
```python
"""Module docstring."""

from typing import Annotated, cast
import pandas as pd
from pydantic import Field
from ecoscope_workflows_core.decorators import task
from ecoscope_workflows_core.annotations import AnyDataFrame


@task
def my_task(
    df: Annotated[AnyDataFrame, Field(description="Input DataFrame.")],
) -> AnyDataFrame:
    """Process the DataFrame."""
    result = df.copy()
    return cast(AnyDataFrame, result)
```

### Export in `__init__.py` (shared library only)
```python
from ._my_task import my_task

__all__ = ["my_task"]
```

---

## Entry Point Registration

### Per-Workflow Tasks (`wt_registry`)
```toml
[project]
name = "my-tasks"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["wt-registry"]

[project.entry-points."wt_registry"]
my_tasks = "my_tasks"
```

No `__init__.py` export needed — the module itself is the entry point.

### Shared Library Tasks (`ecoscope_workflows`)
```toml
[project.entry-points."ecoscope_workflows"]
tasks = "package_name.tasks"
```

No manual registration needed - just export from `__init__.py`.

---

## Error Handling Patterns

```python
# Raise on empty
if raise_on_empty and df.empty:
    raise ValueError("No data returned from source.")

# Input validation
if column not in df.columns:
    raise ValueError(f"Column '{column}' not found.")
```

---

## Docstring Format

```python
@task
def my_task(
    df: Annotated[AnyDataFrame, Field(description="Input data.")],
    column: Annotated[str, Field(description="Column to process.")],
) -> AnyDataFrame:
    """
    Brief one-line description.

    Longer description if needed.

    Args:
        df: The input DataFrame.
        column: Name of the column.

    Returns:
        Modified DataFrame.

    Raises:
        ValueError: If column doesn't exist.
    """
```

---

## Example Tasks

### Config Task
```python
@task
def set_value(
    value: Annotated[str, Field(description="Value to set.")],
) -> str:
    return value
```

### Transformation Task
```python
@task
def filter_rows(
    df: Annotated[AnyDataFrame, Field(description="Input data.")],
    column: Annotated[str, Field(description="Column to filter.")],
    value: Annotated[str, Field(description="Value to keep.")],
) -> AnyDataFrame:
    """Filter DataFrame rows where column equals value."""
    result = df[df[column] == value]
    return cast(AnyDataFrame, result)
```

### I/O Task
```python
@task(tags=["io"])
def fetch_data(
    client: EarthRangerClient,
    time_range: Annotated[TimeRange, Field(description="Time range.")],
    raise_on_empty: Annotated[bool, AdvancedField(default=True)] = True,
) -> DataFrame | EmptyDataFrame:
    """Fetch data from EarthRanger."""
    data = client.get_data(time_range=time_range)
    if raise_on_empty and data.empty:
        raise ValueError("No data returned.")
    return cast(DataFrame, data)
```

---

## Form Schema Customization (Task-Level)

Control how task parameters appear in the rjsf configuration form by using Pydantic annotations.
These changes affect ALL workflows using the task (unlike rjsf-overrides in spec.yaml which are per-workflow).

### Hide Discriminator Fields from Form
Use `Field(exclude=True)` on Literal discriminator fields in BaseModel subclasses.
Keeps Pydantic union discrimination working at runtime, but removes the field from JSON schema.
```python
from pydantic import BaseModel, ConfigDict, Field

class EarthRangerSource(BaseModel):
    model_config = ConfigDict(json_schema_extra={"title": "EarthRanger"})
    source: Annotated[Literal["earthranger"], Field(exclude=True)] = "earthranger"
    name: Annotated[str, Field(description="Source name")]

class LocalFileSource(BaseModel):
    model_config = ConfigDict(json_schema_extra={"title": "Local File"})
    source: Annotated[Literal["local_file"], Field(exclude=True)] = "local_file"
    file_path: Annotated[str, Field(description="Path to file")]
```
Reference: `indexes.py` uses `is_temporal: Annotated[Literal[True], Field(exclude=True)] = True`

### Custom Variant Titles in anyOf Dropdowns
Use `model_config = ConfigDict(json_schema_extra={"title": "Display Name"})` on BaseModel subclasses.
```python
class AutoScale(BaseModel):
    model_config = ConfigDict(json_schema_extra={"title": "Auto-scale"})
    ...

class Custom(BaseModel):
    model_config = ConfigDict(json_schema_extra={"title": "Customize"})
    ...
```
Reference: `_time_density.py` AutoScaleGridCellSize / CustomGridCellSize

### Rename Parameter Labels
Add `Field(title="...")` to the task function parameter annotation.
```python
config: Annotated[
    MyUnionType,
    Field(title="Data Source", description="Select a data source"),
],
```

### Hide Fields with SkipJsonSchema
```python
from pydantic import SkipJsonSchema

# Hide optional None from schema (field still accepts None at runtime)
palette: Annotated[list[str] | SkipJsonSchema[None], Field(...)] = None

# Hide entire field from schema
layer_name: SkipJsonSchema[str] = ""
```
Note: Fields using `SkipJsonSchema` are excluded from Params schema, so they cannot be set via test-cases.yaml.

### Hide Field Labels in Form
Use `title=" "` (single space) to visually hide a field label while keeping it in the schema.
```python
groupers: Annotated[
    UserDefinedGroupers | SkipJsonSchema[None],
    Field(default=None, title=" ", ...),
] = None
```

### Custom Schema Manipulation via Callback
Use `json_schema_extra` with a callback function for advanced schema edits.
```python
def _my_field_schema_extra(schema: dict) -> None:
    schema["items"]["title"] = "Custom Title"

param: Annotated[
    list[Item],
    Field(json_schema_extra=_my_field_schema_extra),
]
```
Reference: `_groupby.py` `_groupers_field_json_schema_extra`

---

## Testing Patterns

```python
def test_my_task():
    df = pd.DataFrame({"col": [1, 2, 3]})
    result = my_task(df)
    assert len(result) == 3

@pytest.fixture
def sample_df():
    return pd.DataFrame({"col": [1, 2, 3]})

@pytest.mark.parametrize("how,expected_len", [
    ("inner", 2),
    ("outer", 4),
])
def test_merge_variants(how, expected_len):
    result = merge_task(df1, df2, how=how)
    assert len(result) == expected_len
```
