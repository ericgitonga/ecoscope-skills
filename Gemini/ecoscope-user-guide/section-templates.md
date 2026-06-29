# Section Templates

Templates for the 8 standard sections of an Ecoscope workflow user guide.

## 1. Introduction

**Purpose**: Briefly explain what the workflow does and who should use it

**Template**:
```markdown
# [Workflow Name] Workflow

## Introduction

This workflow helps you to [primary purpose and goals].

**What this workflow does:**
- Downloads [data type] captured by **[sensor type]** from EarthRanger
- Processes observations including [key measurements]
- Calculates [aggregations/summaries]
- Exports data in multiple formats (CSV, GeoParquet, GPKG)
- Creates interactive charts showing [visualization types]

**Who should use this:**
- Conservation managers monitoring [domain area]
- Researchers analyzing [type of data]
- Anyone needing to export and visualize [sensor type] information stored in EarthRanger
```

**Guidelines**:
- Emphasize the specific sensor type (e.g., TAMHO, Stevens Connect)
- Use bold formatting for sensor names
- Keep descriptions concise and non-technical

---

## 2. Prerequisites

**Purpose**: List requirements before using the workflow

**Template**:
```markdown
## Prerequisites

Before using this workflow, you need:

1. **Ecoscope Desktop** installed on your computer
   - If you haven't installed it yet, please follow the installation instructions for Ecoscope Desktop

2. **EarthRanger Data Source** configured in Ecoscope Desktop
   - You must have already set up a connection to your EarthRanger server
   - Your data source should be configured with proper authentication credentials
   - You'll need to know the name of your configured data source (e.g., "gmmf")

3. **Subject Group with [Sensor Type]** set up in EarthRanger
   - You need to have at least one subject group configured with [sensor type] subjects in your EarthRanger system
   - You'll need to know the exact name of the subject group containing your [sensors/stations]
   - You can find them at https://<your-site>.pamdas.org/admin/observations/subjectgroup/
```

**Guidelines**:
- Always include these 3 prerequisites in order
- Customize prerequisite #3 for the specific EarthRanger data type
- Include the EarthRanger admin URL for subject groups/events

---

## 3. Installation

**Purpose**: Provide step-by-step installation instructions

**Template**:
```markdown
## Installation

1. Select "Workflow Templates" tab
2. Click "+ Add Template"
3. Copy and paste this URL https://github.com/wildlife-dynamics/[workflow-repo-name] and wait for the workflow template to be downloaded and initialized
4. The template will now appear in your available template list
```

**Guidelines**:
- Use exact wording for UI elements
- Always use 4 numbered steps
- Update the GitHub URL to match the workflow repository

---

## 4. Configuration Guide

**Purpose**: Explain all configuration options in detail

**Structure**:
- Basic Configuration (required settings)
- Advanced Configuration (optional settings)

**Basic Configuration Sections**:
1. Workflow Details (name, description)
2. Time Range (since, until, timezone)
3. Data Source (EarthRanger connection)
4. Subject Group (sensor group selection)
5. Group Data (optional grouping)
6. Persist [Data Type] (output formats)
7. Additional workflow-specific settings

**Template for Each Setting**:
```markdown
#### [N]. [Setting Name]
[Brief explanation of what this setting does]

- **[Field Name]** (required/optional): [Description]
  - Example: `[example value]`
  - Note: [Any warnings or special considerations]
```

**Advanced Configuration Template**:
```markdown
### Advanced Configuration

These optional settings provide additional control over your workflow:

#### Filename Prefixes
Customize the names of your output files.

- **[Task Name] - Filename Prefix**: Custom prefix for [file type]
  - Default: `"[default_value]"`
  - Example: `"[example_prefix]"` will create files like `[example_prefix]_abc123.csv`
```

**Guidelines**:
- Number basic configuration sections (1-7+)
- Use "(required)" or "(optional)" for each field based on rjsf.json
- Always provide concrete examples from test-cases.yaml
- Include relevant warnings from rjsf.json descriptions
- Mark advanced settings with "Advanced Configuration" header

---

## 5. Running the Workflow

**Purpose**: Explain how to execute the workflow

**Template**:
```markdown
## Running the Workflow

Once you've configured all the settings:

1. **Review your configuration**
   - Double-check your time range, data source, and subject group name

2. **Save and run**
   - Click the "Submit" and the workflow will show up in "My Workflows" table button in Ecoscope Desktop
   - Click on "Run" and the workflow will begin processing

3. **Monitor progress and wait for completion**
   - You'll see status updates as the workflow runs
   - Processing time depends on:
     - The size of your date range
     - Number of [sensors/stations/subjects]
     - Number of observations in the system
   - The workflow completes with status "Success" or "Failed"
```

**Guidelines**:
- Always use these 3 numbered steps
- Customize the monitoring bullets for the workflow type
- Keep language consistent across workflows

---

## 6. Understanding Your Results

**Purpose**: Explain output files and visualizations

**Structure**:
- Data Outputs (files)
- Visual Outputs (dashboard/charts)
- Grouped Outputs (if applicable)

**Data Outputs Template**:
```markdown
## Understanding Your Results

After the workflow completes successfully, you'll find your outputs in the designated output folder.

### Data Outputs

Your [data type] will be saved in the format(s) you selected:

#### [Output Type] Data

- **File formats**: CSV, GeoParquet, and/or GPKG (based on your selection)
- **Opens in**: Microsoft Excel, Google Sheets (CSV), Python/R (GeoParquet), QGIS/ArcGIS (GPKG)
- **Best for**:
  - CSV: Quick data review and analysis
  - GeoParquet: Large datasets, programmatic analysis
  - GPKG: Spatial analysis in GIS software
- **Contents**: [Description of data with key columns]
  - `column_name`: Description
  - `another_column`: Description
```

**Visual Outputs Template**:
```markdown
### Visual Outputs (Dashboard)

The workflow creates an interactive dashboard with [N] main visualizations:

#### [Chart Name]
- **Format**: Interactive line chart
- **Features**:
  - X-axis: [axis description]
  - Y-axis: [axis description]
  - [Additional features like shape, hover, legend]
  - Interactive hover: Shows exact values when you mouse over data points
```

**Guidelines**:
- Describe both raw and aggregated data outputs
- List key columns from the workflow's data transformations
- Describe chart types and their features
- Reference spec.yaml for chart configurations (shape, layout)

---

## 7. Common Use Cases & Examples

**Purpose**: Provide practical configuration examples

**Template**:
```markdown
## Common Use Cases & Examples

Here are some typical scenarios and how to configure the workflow for each:

### Example 1: [Use Case Name]
**Goal**: [What the user wants to achieve]

**Configuration**:
- **Time Range**:
  - Since: `YYYY-MM-DDTHH:MM:SS`
  - Until: `YYYY-MM-DDTHH:MM:SS`
  - Timezone: `[timezone]`
- **Subject Group Name**: `"[group name]"`
- **[Other Key Settings]**: [values]

**Result**:
- [Description of outputs]
- [Description of visualizations]

---
```

**Guidelines**:
- Include 3-4 examples minimum
- Base examples on test-cases.yaml configurations
- Cover simple, grouped, and filtered scenarios
- Use horizontal rules (---) between examples
- Always show complete configurations with realistic dates

---

## 8. Troubleshooting

**Purpose**: Help users resolve common issues

**Categories of Issues**:
1. Workflow fails to start (authentication/connectivity)
2. No observations returned (date range/subject group)
3. Workflow runs very slowly (performance)
4. Authentication errors (permissions)
5. Charts/visualizations issues (empty/missing data)
6. Missing measurement data (sensor-specific)

**Template**:
```markdown
## Troubleshooting

### Common Issues and Solutions

#### [Issue Name]
**Problem**: [Description of the problem]

**Solutions**:
- [Solution 1]
- [Solution 2]
- [Solution 3]
```

**Guidelines**:
- Include 6+ common issues
- Customize issue #6 for workflow-specific measurements
- Reference EarthRanger admin URLs for verification
- Include the "warm-up" note for performance issues
- Provide actionable solutions, not just explanations
