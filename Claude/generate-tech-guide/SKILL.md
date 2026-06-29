---
name: generate-tech-guide
description: Generate a PDF technical guide for an ecoscope workflow using ReportLab in the ds conda env.
argument-hint: [repo-name]
---

# Generate Technical Guide Skill

Generate a styled PDF technical guide for an ecoscope workflow. The guide documents
methodology, data flow, output specifications, and software versions — formatted to
match the PGAFF technical guide style (dark green headers, amber top bar, alternating
table rows).

## Usage

```
/generate-tech-guide <repo-name>
```

- Target repo: `/home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS`
- Output: `docs/technical_guide.pdf` inside the repo
- Generation script: `docs/generate_technical_guide.py` (kept alongside PDF)

## PDF Tooling

Always use **ReportLab** via the `ds` conda environment:

```bash
conda run -n ds python docs/generate_technical_guide.py
```

Never use weasyprint — it has known rendering issues with the required table and
heading styles. ReportLab in `ds` has been verified to produce correct output.

## Reference Template

Use the geofence-crossing generation script as the style template:

```
/home/gitonga/Develop/PGAFF/repos/extras/wt-geofence-crossing/technical_guide/generate_technical_guide.py
```

Study it before writing the new script — reuse the colour palette, style definitions,
`make_table`, `on_page`, and helper functions verbatim. Only change the content.

Also use the custom-events script as a second reference for bundled-tasks workflows:

```
/home/gitonga/Develop/PGAFF/repos/wt/wt-custom-events/docs/generate_technical_guide.py
```

## Colour Palette (do not change)

```python
GREEN_DARK  = colors.HexColor("#115631")
GREEN_MID   = colors.HexColor("#2d6a4f")
AMBER       = colors.HexColor("#e7a553")
SLATE       = colors.HexColor("#3d3d3d")
LIGHT_GREY  = colors.HexColor("#f5f5f5")
MID_GREY    = colors.HexColor("#cccccc")
```

## Script Location

Place the script at `docs/generate_technical_guide.py` inside the workflow repo.
Set `OUTPUT_FILE` using `os.path.dirname(__file__)` so the PDF is always written
next to the script regardless of where the script is invoked from:

```python
import os
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "technical_guide.pdf")
```

## Required Sections

Every technical guide must cover these sections in order:

| # | Section | Content |
|---|---|---|
| 1 | Overview | What the workflow does; key distinguishing feature |
| 2 | Dependencies & Prerequisites | ER connection params, groupers, base maps, any custom resolvers |
| 3 | Data Ingestion Pipeline | Fetch tasks, timezone handling, any column extraction |
| 4 | Core Algorithm | The main analytical step(s) — crossing detection, status grouping, etc. |
| 5 | Processing Pipeline | Filtering, indexing, colouring, column renaming |
| 6 | Dashboard Outputs | One subsection per widget — layer spec, colour, tooltip, legend |
| 7 | Interactive Dashboard | gather_dashboard wiring, widget table, grouper/dropdown behaviour |
| 8 | Output Files | All files written to `$ECOSCOPE_WORKFLOWS_RESULTS` |
| 9 | Workflow Execution Logic | Skip conditions, data flow summary table |
| 10 | Software Versions | Package, version, role — include bundled tasks if present |

## README Link

After generating the PDF, ensure `README.md` links to it:

```markdown
For full configuration reference, methodology, and troubleshooting see the [Technical Guide](docs/technical_guide.pdf).
```

## Workflow Steps

### 1. Read the spec.yaml and task source

```bash
cat /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/spec.yaml
find /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS -name "*.py" \
  ! -path "*/.pixi/*" ! -path "*/tests/*" | sort
```

Read every task Python file to understand the exact algorithm before writing.

### 2. Write the generation script

Create `docs/generate_technical_guide.py`. Copy the style boilerplate from the
reference template exactly — palette, styles, `make_table`, `on_page`, `build`
skeleton. Then fill in the content for each section based on what you read.

### 3. Run the script

```bash
mkdir -p /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/docs
conda run -n ds python \
  /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/docs/generate_technical_guide.py
```

Verify the PDF was written:

```bash
ls -lh /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS/docs/technical_guide.pdf
```

### 4. Update README

Ensure the Documentation section in `README.md` links to `docs/technical_guide.pdf`.

### 5. Commit

```bash
git -C /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS add \
  docs/generate_technical_guide.py docs/technical_guide.pdf README.md
git -C /home/gitonga/Develop/PGAFF/repos/wt/wt-$ARGUMENTS \
  commit -m "docs: add technical guide PDF"
```

## Notes

- Never commit `docs/technical_guide.md` — the PDF is the deliverable
- The generation script is committed alongside the PDF so the guide can be regenerated
  when the workflow changes
- If the workflow has bundled custom tasks, document them in Section 4 using the
  custom-events guide as a model
- Column widths in `make_table` must sum to ≤ 16.5 cm (A4 with 2 cm margins each side)
