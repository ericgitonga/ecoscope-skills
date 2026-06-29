# Ecoscope Workflow Patterns

Reference for creating workflows. For spec.yaml syntax, see [ecoscope-spec.md](ecoscope-spec.md).

---

## Workflow Repository Structure

```
wt-<workflow-name>/
├── spec.yaml              # Workflow definition
├── layout.json            # Dashboard widget layout
├── test-cases.yaml        # Test case definitions
├── pixi.toml              # Dependencies for compilation
├── dev/
│   ├── recompile.sh       # Recompile workflow
│   └── pytest-cli.sh      # Run tests locally
├── resources/templates/   # Optional: templates, data
├── .github/workflows/     # CI/CD
└── ecoscope-workflows-<name>-workflow/  # Generated
```

---

## Common Workflow Patterns

### 1. Setup Tasks (Always First)

```yaml
workflow:
  - name: Workflow Details
    id: workflow_details
    task: set_workflow_details

  - name: Time Range
    id: time_range
    task: set_time_range
    partial:
      time_format: "%d %b %Y %H:%M:%S %Z"

  - name: Extract Timezone
    id: get_timezone
    task: get_timezone_from_time_range
    partial:
      time_range: ${{ workflow.time_range.return }}

  - name: Data Source
    id: er_client_name
    task: set_er_connection
```

### 2. Data Fetching

```yaml
  # EarthRanger events
  - name: Get Events
    id: get_event_data
    task: get_events
    partial:
      client: ${{ workflow.er_client_name.return }}
      time_range: ${{ workflow.time_range.return }}
      raise_on_empty: false

  # Subject observations
  - name: Get Subject Observations
    id: subject_obs
    task: get_subjectgroup_observations
    partial:
      client: ${{ workflow.er_client_name.return }}
      time_range: ${{ workflow.time_range.return }}

  # External files (custom extension)
  - name: Load Data
    id: load_data
    task: load_df
    partial:
      deserialize_json: false
```

### 3. Data Processing (Task Group)

```yaml
  - title: Process Data
    type: task-group
    description: "Process data by applying filters, transformations."
    tasks:
      - name: Convert to Timezone
        id: convert_tz
        task: convert_values_to_timezone
        partial:
          df: ${{ workflow.get_data.return }}
          timezone: ${{ workflow.get_timezone.return }}
          columns: ["time"]

      - name: Normalize JSON Column
        id: normalize_details
        task: normalize_json_column
        partial:
          df: ${{ workflow.convert_tz.return }}
          column: "event_details"

      - name: Filter Data
        id: filter_data
        task: apply_reloc_coord_filter
        partial:
          df: ${{ workflow.normalize_details.return }}

      - name: Apply SQL Query
        id: sql_query
        task: apply_sql_query
        partial:
          df: ${{ workflow.filter_data.return }}
```

### 4. Grouping and Splitting

```yaml
  - name: Set Groupers
    id: groupers
    task: set_groupers

  - name: Add Temporal Index
    id: temporal_index
    task: add_temporal_index
    partial:
      df: ${{ workflow.sql_query.return }}
      groupers: ${{ workflow.groupers.return }}

  - name: Split by Group
    id: split_groups
    task: split_groups
    partial:
      df: ${{ workflow.temporal_index.return }}
      groupers: ${{ workflow.groupers.return }}
```

### 5. Map Generation Pattern

```yaml
  - title: Generate Maps
    type: task-group
    tasks:
      - name: Apply Colormap
        id: colormap
        task: apply_color_map
        partial:
          input_column_name: "category"
          colormap: "tab20b"
        mapvalues:
          argnames: df
          argvalues: ${{ workflow.split_groups.return }}

      - name: Set Base Maps
        id: base_map_defs
        task: set_base_maps

      - name: Create Map Layer
        id: map_layer
        task: create_point_layer
        partial:
          layer_style:
            fill_color_column: "category_colormap"
            get_radius: 5
        mapvalues:
          argnames: geodataframe
          argvalues: ${{ workflow.colormap.return }}

      - name: Draw Ecomap
        id: ecomap
        task: draw_ecomap
        partial:
          tile_layers: ${{ workflow.base_map_defs.return }}
        mapvalues:
          argnames: geo_layers
          argvalues: ${{ workflow.map_layer.return }}

      - name: Persist Ecomap
        id: ecomap_html_url
        task: persist_text
        partial:
          root_path: ${{ env.ECOSCOPE_WORKFLOWS_RESULTS }}
        mapvalues:
          argnames: text
          argvalues: ${{ workflow.ecomap.return }}

      - name: Create Map Widget
        id: map_widget
        task: create_map_widget_single_view
        map:
          argnames: [view, data]
          argvalues: ${{ workflow.ecomap_html_url.return }}

      - name: Merge Widget Views
        id: merged_map_widget
        task: merge_widget_views
        partial:
          widgets: ${{ workflow.map_widget.return }}
```

### 6. Chart Generation Pattern

```yaml
  - name: Draw Chart
    id: chart
    task: draw_line_chart
    partial:
      x_column: date
      y_column: value
    mapvalues:
      argnames: dataframe
      argvalues: ${{ workflow.data.return }}

  - name: Persist Chart
    id: persist_chart
    task: persist_text
    partial:
      root_path: ${{ env.ECOSCOPE_WORKFLOWS_RESULTS }}
    mapvalues:
      argnames: text
      argvalues: ${{ workflow.chart.return }}

  - name: Create Chart Widget
    id: chart_widget
    task: create_plot_widget_single_view
    map:
      argnames: [view, data]
      argvalues: ${{ workflow.persist_chart.return }}
```

### 7. Dashboard Assembly (Always Last)

```yaml
  - name: Create Dashboard
    id: dashboard
    task: gather_dashboard
    partial:
      details: ${{ workflow.workflow_details.return }}
      widgets:
        - ${{ workflow.merged_map_widget.return }}
        - ${{ workflow.merged_chart_widget.return }}
      groupers: ${{ workflow.groupers.return }}
      time_range: ${{ workflow.time_range.return }}
```

---

## Polyline Layer Style

Different from point layers:

```yaml
layer_style:
  get_color_column: category_colormap  # not fill_color_column
  get_width: 2                          # not get_radius
```

---

## layout.json Structure

```json
[
    {
        "i": "0",
        "x": 0, "y": 0,
        "w": 10, "h": 12,
        "minW": 5, "minH": 10,
        "widget_id": 0,
        "static": false
    }
]
```

---

## test-cases.yaml Structure

```yaml
base:
  name: Base Test Case
  mock_io: true                 # true = mock I/O, false = real API
  params:
    workflow_details:
      name: "Workflow Name"
    time_range:
      since: "2025-01-01T00:00:00Z"
      until: "2025-01-31T23:59:59Z"
    er_client_name:
      data_source:
        name: "connection_name"
    groupers:
      groupers: []              # Empty = no grouping

with_grouper:
  name: With Grouper
  mock_io: false
  params:
    groupers:
      groupers:
        - "category_column"     # Value grouper
        - "%B"                  # Temporal grouper (month)
```

---

## pixi.toml Structure

Note: `wt-compiler` manages compilation via its own ephemeral environment from `spec.yaml` requirements — no `[feature.compile.dependencies]` or compile environment needed.

```toml
[workspace]
name = "wt-<workflow-name>"
channels = [
    'https://repo.prefix.dev/ecoscope-workflows/',
    'https://repo.prefix.dev/ecoscope-workflows-custom/',
    'conda-forge',
]
platforms = ['linux-64', 'osx-arm64', 'osx-64', 'win-64']

[dependencies]
curl = "*"
rattler-build = "*"
yq = "*"
hatch = "*"
pip = "*"
hatch-vcs = "*"
```

## spec.yaml Requirements Formats

```yaml
# New (ecoscope-platform >= 2.11 — preferred for new workflows)
requirements:
  - name: ecoscope-platform
    version: ">=2.11.0, <3"
    channel: https://repo.prefix.dev/ecoscope-workflows/
  - name: ecoscope-workflows-ext-custom   # PGAFF shared task library
    version: ">=0.1.0, <1.0.0"
    channel: https://repo.prefix.dev/ecoscope-workflows-custom/
  - name: my-tasks                         # local dev tasks (optional)
    path: /absolute/path/to/my-tasks
    editable: true

# Legacy (ecoscope-workflows-core + ext-ecoscope)
requirements:
  - name: ecoscope-workflows-core
    version: ">=0.22.18, <0.23.0"
    channel: https://repo.prefix.dev/ecoscope-workflows/
  - name: ecoscope-workflows-ext-ecoscope
    version: ">=0.22.18, <0.23.0"
    channel: https://repo.prefix.dev/ecoscope-workflows/
```

---

## Common Tasks Reference

### Data Sources
- `set_er_connection` - EarthRanger
- `set_gee_connection` - Google Earth Engine

### Data Fetching
- `get_events`, `get_subjectgroup_observations`, `get_patrols`
- `download_roi` - ROI/boundaries
- `load_df` - External files (custom)

### Data Processing
- `map_columns` - Rename, drop, retain columns
- `apply_sql_query` - SQL filtering
- `normalize_json_column` - Flatten nested JSON
- `drop_column_prefix` - Remove prefixes
- `apply_reloc_coord_filter` - Filter coordinates
- `convert_values_to_timezone` - Timezone conversion
- `add_temporal_index`, `split_groups` - Grouping

### Visualization
- `apply_color_map` - Color mapping
- `create_point_layer`, `create_polyline_layer` - Map layers
- `draw_ecomap` - Render map
- `draw_line_chart` - Charts
- `create_map_widget_single_view`, `create_plot_widget_single_view`
- `merge_widget_views` - Combine grouped widgets

### Utilities
- `set_string_var`, `set_bool_var` - Variables
- `set_groupers` - Configure groupers
- `maybe_skip_df` - Conditional skip
- `persist_df_wrapper`, `persist_text` - Save outputs

---

## Testing Commands

```bash
./dev/pytest-cli.sh <workflow> --case <case> --local --quiet  # Single case
./dev/pytest-cli.sh <workflow> --all --local --quiet          # All cases
```
