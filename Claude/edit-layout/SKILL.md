---
name: edit-layout
description: Edit dashboard layout.json for workflow widgets. Use when adding or repositioning dashboard visualizations.
argument-hint: [workflow-name]
disable-model-invocation: true
---

# Edit Dashboard Layout

Update widget positions in `layout.json` for workflow `wt-$ARGUMENTS`.

## Prerequisites

Only applicable if workflow has a `gather_dashboard` task. Check spec.yaml first.

## Step 1: Review Current Layout

```bash
cat /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/layout.json
```

## Step 2: Identify Widget Changes

Check spec.yaml for dashboard widget order:
- Each `draw_*` task output that feeds into `gather_dashboard` is a widget
- `widget_id` corresponds to order in `dashboard.widgets[]`

## Step 3: Add/Update Widget Positions

Widget template:
```json
{
    "i": "<index>",
    "x": 0,
    "y": <row>,
    "widget_id": <widget_index>,
    "w": 10,
    "h": 12,
    "minW": 5,
    "minH": 10,
    "static": false
}
```

## Positioning Guidelines

| Property | Description |
|----------|-------------|
| `i` | Unique string identifier |
| `x`, `y` | Grid position (y increments by h for stacking) |
| `widget_id` | Index matching dashboard.widgets[] order |
| `w`, `h` | Width and height in grid units |
| `minW`, `minH` | Minimum dimensions |

**Standard layouts:**
- Full width: `w: 10, h: 12`
- Side by side: `w: 5, h: 12` (two widgets with x: 0 and x: 5)
- Tall chart: `w: 10, h: 16`

**Stacking widgets:**
- First widget: `y: 0`
- Second widget: `y: 12` (previous y + previous h)
- Third widget: `y: 24`

## Supervision Checkpoints

Ask for approval before:
- Modifying layout.json
