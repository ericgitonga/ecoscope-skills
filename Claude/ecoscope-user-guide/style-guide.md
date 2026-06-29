# Style Guide

Formatting and language guidelines for Ecoscope workflow user guides.

## Formatting Rules

### Bold (`**text**`)
Use for:
- Sensor names (e.g., **TAMHO**, **Stevens Connect**)
- Field labels in configuration
- File format types
- Section headers within lists

### Code Formatting (`` `text` ``)
Use for:
- Example values
- Column names
- File names
- Time formats
- Configuration keys

### Italics
Use sparingly, only for emphasis.

---

## Language Guidelines

- Write for non-technical users
- Use active voice
- Be concise but complete
- Avoid jargon without explanation
- Use consistent terminology throughout

### Terminology Consistency
| Use This | Not This |
|----------|----------|
| workflow | process, pipeline |
| configuration | settings, parameters |
| data source | connection, server |
| subject group | subject set, group |

---

## Common Patterns

### Time Range Examples
```markdown
- **Since**: `2025-11-20T00:00:00`
- **Until**: `2025-12-25T23:59:59`
- **Timezone**: `Africa/Nairobi (UTC+03:00)` or `UTC (UTC+00:00)`
```

### Grouper Options
- Temporal: `"%Y"` (Year), `"%B"` (Month), `"%Y-%m-%d"` (Date)
- Category: `"weather_station"`, `"sensor"`, `"event_type"`, etc.

### File Format Descriptions
Always describe in this order:
1. **CSV**: Quick review in spreadsheets
2. **GeoParquet**: Efficient for large datasets, programmatic analysis
3. **GPKG**: GIS software compatibility

### EarthRanger URLs
- Subject groups: `https://<your-site>.pamdas.org/admin/observations/subjectgroup/`
- Event types: `https://<your-site>.pamdas.org/admin/activity/eventtype/`

---

## Warnings and Notes

- Use "Note:" for additional context
- Place warnings inline with relevant configuration items
- Be specific about consequences

Example:
```markdown
- **Subject Group Name** (required): The exact name of your subject group
  - Note: This must match exactly, including capitalization
```

---

## Examples Best Practices

- Always use realistic dates (not placeholder dates)
- Base examples on test-cases.yaml
- Show complete configurations, not partial ones
- Explain the expected result for each example

---

## Quality Checklist

Before finalizing the user guide:

- [ ] All 8 sections are present and complete
- [ ] Examples use realistic dates and values from test-cases.yaml
- [ ] Sensor names are bolded consistently
- [ ] Code examples use proper formatting
- [ ] All configuration fields from rjsf.json are documented
- [ ] Troubleshooting includes workflow-specific issues
- [ ] EarthRanger admin URLs are included where relevant
- [ ] Charts/visualizations match spec.yaml configurations
- [ ] Column names match spec.yaml transformations
- [ ] Language is non-technical and user-friendly
- [ ] Examples show complete configurations
- [ ] File format descriptions are consistent
- [ ] Timezone examples are realistic
