---
name: ecoscope-user-guide
description: Create user documentation for ecoscope workflows. Use when writing README.md for workflow repos.
argument-hint: [workflow-name]
disable-model-invocation: true
---

# Create Ecoscope Workflow User Guide

Create comprehensive documentation for non-technical users.

## Required Source Files
1. `spec.yaml` - Task definitions and data flow
2. `test-cases.yaml` - Example configurations
3. `rjsf.json` - Form schema with field descriptions
4. `README.md` - Target output file

## Process

### 1. Analyze Workflow
Read source files from workflow directory:
```bash
cat /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/spec.yaml
cat /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/test-cases.yaml
cat /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/ecoscope-workflows-*-workflow/ecoscope_workflows_*_workflow/rjsf.json
```

Identify workflow type (Climate, Hydrological, Event, Subject).

### 2. Write 8 Sections
Follow templates in [section-templates.md](section-templates.md):
1. Introduction
2. Prerequisites
3. Installation
4. Configuration Guide
5. Running the Workflow
6. Understanding Your Results
7. Common Use Cases & Examples
8. Troubleshooting

### 3. Apply Style Guide
Use conventions from [style-guide.md](style-guide.md):
- Formatting rules (bold, code, italics)
- Language guidelines
- Common patterns (time range, groupers, file formats)

### 4. Review Checklist
Before finalizing:
- [ ] All 8 sections present and complete
- [ ] Examples use realistic dates from test-cases.yaml
- [ ] All rjsf.json fields documented
- [ ] Troubleshooting includes workflow-specific issues
- [ ] Language is non-technical and user-friendly

## Reference Files
- [Section Templates](section-templates.md) - Standard 8-section structure
- [Style Guide](style-guide.md) - Formatting and language rules

## Supervision Checkpoints

Ask for approval before:
- Writing README.md
- Making assumptions about workflow domain
