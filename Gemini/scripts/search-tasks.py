#!/usr/bin/env python3
"""
Search for available tasks in ecoscope workflow task libraries.

Usage:
    ./search-tasks.py                      # List all tasks
    ./search-tasks.py <keyword>            # Search tasks by keyword
    ./search-tasks.py -s <task_name>       # Show task signature and docstring
    ./search-tasks.py --lib <path> [...]   # Add custom task library paths

Examples:
    ./search-tasks.py event
    ./search-tasks.py -s get_events
    ./search-tasks.py --lib /path/to/my/tasks event
"""

import ast
import sys
from pathlib import Path
from dataclasses import dataclass

# Default task library paths
DEFAULT_TASK_LIBRARIES = {
    "core": Path("/home/gitonga/Develop/PGAFF/repos/ecoscope-workflows/src/ecoscope-workflows-core/ecoscope_workflows_core/tasks"),
    "ecoscope": Path("/home/gitonga/Develop/PGAFF/repos/ecoscope-workflows/src/ecoscope-workflows-ext-ecoscope/ecoscope_workflows_ext_ecoscope/tasks"),
    "custom": Path("/home/gitonga/Develop/PGAFF/repos/ecoscope-workflow-task-library/src/ecoscope-workflows-ext-custom/ecoscope_workflows_ext_custom/tasks"),
}

# Colors
GREEN = "\033[0;32m"
BLUE = "\033[0;34m"
YELLOW = "\033[0;33m"
CYAN = "\033[0;36m"
MAGENTA = "\033[0;35m"
NC = "\033[0m"

LIB_COLORS = {"core": GREEN, "ecoscope": BLUE, "custom": YELLOW}


@dataclass
class TaskInfo:
    name: str
    module: str
    library: str
    file_path: Path
    lineno: int
    signature: str = ""
    docstring: str = ""


def file_to_module(file_path: Path, tasks_dir: Path) -> str:
    """Convert file path to Python module path."""
    try:
        rel_path = file_path.relative_to(tasks_dir.parent)
        module = str(rel_path).replace("/", ".").replace(".py", "")
        # Remove leading underscore from filename
        parts = module.split(".")
        parts[-1] = parts[-1].lstrip("_")
        return ".".join(parts)
    except ValueError:
        return file_path.stem


def extract_tasks_from_file(file_path: Path, lib_name: str, tasks_dir: Path) -> list[TaskInfo]:
    """Extract all @task decorated functions from a file."""
    tasks = []

    try:
        source = file_path.read_text()
        tree = ast.parse(source)
    except Exception:
        return tasks

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        # Check for @task decorator
        has_task_decorator = any(
            (isinstance(d, ast.Name) and d.id == "task")
            or (isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id == "task")
            for d in node.decorator_list
        )

        if not has_task_decorator:
            continue

        # Extract function signature
        lines = source.split("\n")

        # Extract signature lines (from def to ):)
        sig_lines = []
        for i in range(node.lineno - 1, min(node.end_lineno, len(lines))):
            sig_lines.append(lines[i])
            if "):" in lines[i] or ") ->" in lines[i]:
                break

        signature = "\n".join(sig_lines)

        # Get docstring
        docstring = ast.get_docstring(node) or ""

        tasks.append(
            TaskInfo(
                name=node.name,
                module=file_to_module(file_path, tasks_dir),
                library=lib_name,
                file_path=file_path,
                lineno=node.lineno,
                signature=signature,
                docstring=docstring,
            )
        )

    return tasks


def get_all_tasks(task_libraries: dict[str, Path]) -> list[TaskInfo]:
    """Get all tasks from all libraries."""
    all_tasks = []

    for lib_name, lib_path in task_libraries.items():
        if not lib_path.exists():
            continue

        for py_file in lib_path.rglob("*.py"):
            if py_file.name == "__init__.py" or "__pycache__" in str(py_file):
                continue

            all_tasks.extend(extract_tasks_from_file(py_file, lib_name, lib_path))

    return sorted(all_tasks, key=lambda t: (t.library, t.module, t.name))


def get_lib_color(lib_name: str) -> str:
    """Get color for a library, with fallback for custom libs."""
    return LIB_COLORS.get(lib_name, MAGENTA)


def list_all_tasks(task_libraries: dict[str, Path]):
    """List all available tasks grouped by library."""
    tasks = get_all_tasks(task_libraries)

    if not tasks:
        print("No tasks found.")
        return

    current_lib = None
    current_module = None

    for task in tasks:
        color = get_lib_color(task.library)

        if task.library != current_lib:
            if current_lib is not None:
                print()
            print(f"{color}━━━ [{task.library}] ━━━{NC}")
            current_lib = task.library
            current_module = None

        if task.module != current_module:
            print(f"  {CYAN}{task.module}{NC}")
            current_module = task.module

        print(f"    {color}{task.name}{NC}")


def search_tasks(keyword: str, task_libraries: dict[str, Path]):
    """Search tasks by keyword."""
    tasks = get_all_tasks(task_libraries)
    keyword_lower = keyword.lower()

    matches = [t for t in tasks if keyword_lower in t.name.lower()]

    if not matches:
        print(f"No tasks found matching: {keyword}")
        return

    print(f"{BLUE}Tasks matching '{keyword}':{NC}\n")

    current_lib = None
    for task in matches:
        color = get_lib_color(task.library)

        if task.library != current_lib:
            if current_lib is not None:
                print()
            print(f"{color}[{task.library}]{NC}")
            current_lib = task.library

        print(f"  {color}{task.name}{NC}")
        print(f"    └─ {CYAN}{task.module}{NC}")


def show_signature(task_name: str, task_libraries: dict[str, Path]):
    """Show task signature and docstring."""
    tasks = get_all_tasks(task_libraries)

    matches = [t for t in tasks if t.name == task_name]

    if not matches:
        # Try partial match
        partial = [t for t in tasks if task_name.lower() in t.name.lower()]
        if partial:
            print(f"Task '{task_name}' not found. Did you mean:\n")
            for t in partial[:5]:
                print(f"  - {t.name}")
        else:
            print(f"Task not found: {task_name}")
        return

    task = matches[0]
    color = get_lib_color(task.library)

    print(f"{GREEN}Task:{NC}    {task.name}")
    print(f"{GREEN}Library:{NC} {task.library}")
    print(f"{GREEN}Module:{NC}  {task.module}")
    print(f"{GREEN}File:{NC}    {task.file_path}:{task.lineno}")
    print()
    print(f"{CYAN}Signature:{NC}")
    print("─" * 60)
    print(task.signature)
    print("─" * 60)

    if task.docstring:
        print()
        print(f"{CYAN}Docstring:{NC}")
        print("─" * 60)
        print(task.docstring)
        print("─" * 60)


def print_help():
    print(__doc__)


def parse_args(args: list[str]) -> tuple[dict[str, Path], list[str]]:
    """Parse command line arguments, extracting --lib options."""
    task_libraries = dict(DEFAULT_TASK_LIBRARIES)
    remaining_args = []
    custom_lib_count = 0

    i = 0
    while i < len(args):
        if args[i] in ("--lib", "-l"):
            if i + 1 >= len(args):
                print("Error: --lib requires a path argument")
                sys.exit(1)
            lib_path = Path(args[i + 1]).expanduser().resolve()
            if not lib_path.exists():
                print(f"Warning: Library path does not exist: {lib_path}")
            else:
                custom_lib_count += 1
                lib_name = f"lib{custom_lib_count}"
                task_libraries[lib_name] = lib_path
            i += 2
        else:
            remaining_args.append(args[i])
            i += 1

    return task_libraries, remaining_args


def main():
    task_libraries, args = parse_args(sys.argv[1:])

    if not args:
        list_all_tasks(task_libraries)
    elif args[0] in ("-h", "--help"):
        print_help()
    elif args[0] in ("-s", "--signature"):
        if len(args) < 2:
            print("Usage: ./search-tasks.py -s <task_name>")
            sys.exit(1)
        show_signature(args[1], task_libraries)
    else:
        search_tasks(args[0], task_libraries)


if __name__ == "__main__":
    main()
