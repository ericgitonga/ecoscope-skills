# Ecoscope Workflow Development

Entry point for ecoscope workflow development context.

## Repositories

- `/home/gitonga/Develop/PGAFF/repos/ecoscope-workflows` - Compiler + core task libraries
- `/home/gitonga/Develop/PGAFF/repos/ecoscope` - Base ecoscope library
- `/home/gitonga/Develop/PGAFF/repos/ecoscope-workflow-task-library` - Custom task library
- `/home/gitonga/Develop/PGAFF/repos/wt/*` - Individual workflow repos

## Task Library Locations

1. `ecoscope-workflows/src/ecoscope-workflows-ext-ecoscope/.../tasks`
2. `ecoscope-workflow-task-library/src/ecoscope-workflows-ext-custom/.../tasks`
3. `ecoscope-workflows/src/ecoscope-workflows-core/.../tasks`

## Scripts

- `/home/gitonga/Develop/PGAFF/repos/ecoscope-skills/scripts/scaffold.sh <wt-name>` - Scaffold new workflow repo
- `/home/gitonga/Develop/PGAFF/repos/ecoscope-skills/scripts/search-tasks.py` - Search task libraries
  - No args: list all tasks
  - `<keyword>`: search by keyword
  - `-s <task_name>`: show task signature and docstring
  - `--lib <path>`: add custom task library path

## Commands

```bash
# Compile + test (wt-compiler)
cd /home/gitonga/Develop/PGAFF/repos/wt/<workflow> && wt-compiler compile --spec spec.yaml --pkg-name-prefix=ecoscope-workflows --results-env-var=ECOSCOPE_WORKFLOWS_RESULTS --clobber --update && ./dev/pytest-cli.sh <workflow> --case <case> --local --quiet
```

## Workflow Development Process

1. Define workflow in `spec.yaml` → see [ecoscope-spec.md](ecoscope-spec.md)
2. Check existing tasks in the 3 task libraries
3. Implement/modify tasks if needed → see [ecoscope-tasks.md](ecoscope-tasks.md)
4. Test and review output
5. Fine-tune rjsf-overrides and layout.json

## Validation by Change Type

- **Logic/task changes**: Compile → run tests (`pytest-cli.sh`)
- **Configuration form changes** (rjsf-overrides, defaults, UI): Compile → manually validate the generated rjsf form

## Related References

- [ecoscope-spec.md](ecoscope-spec.md) - spec.yaml structure and syntax
- [ecoscope-workflow-patterns.md](ecoscope-workflow-patterns.md) - Common workflow patterns
- [ecoscope-tasks.md](ecoscope-tasks.md) - Task implementation guide
- [ecoscope-compiler.md](ecoscope-compiler.md) - Compiler internals
