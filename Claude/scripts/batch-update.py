#!/usr/bin/env python3
"""
Batch update ecoscope workflow repositories.

Usage:
    ./batch-update.py sync [--dry-run] [--commit]
    ./batch-update.py bump --core VER --ext-ecoscope VER --ext-custom VER [--dry-run] [--commit]
    ./batch-update.py run -- <command> [args...]

Examples:
    ./batch-update.py sync --dry-run
    ./batch-update.py bump --core ">=0.23.0,<0.24" --ext-custom ">=0.0.30, <0.1.0"
    ./batch-update.py bump --core ">=0.23.0,<0.24" --commit
    ./batch-update.py run -- ./dev/recompile.sh --local
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from difflib import unified_diff
from pathlib import Path

import yaml

# --- Colors ---
GREEN = "\033[0;32m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
YELLOW = "\033[0;33m"
CYAN = "\033[0;36m"
BOLD = "\033[1m"
NC = "\033[0m"

DEFAULT_CONFIG = Path(__file__).parent / "batch-config.yaml"

# Dependency name mapping for bump command
DEP_NAMES = {
    "core": "ecoscope-workflows-core",
    "ext_ecoscope": "ecoscope-workflows-ext-ecoscope",
    "ext_custom": "ecoscope-workflows-ext-custom",
}


def load_config(config_path: Path) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def get_git_branch(repo_path: Path) -> str | None:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def git_commit(repo_path: Path, message: str) -> bool:
    branch = get_git_branch(repo_path)
    if branch is None:
        print(f"    {RED}Not a git repo, skipping commit{NC}")
        return False
    if branch == "main":
        print(f"    {RED}On main branch, refusing to commit{NC}")
        return False

    # Stage all changes
    subprocess.run(["git", "add", "-A"], cwd=repo_path, capture_output=True)

    # Check if there are staged changes
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=repo_path, capture_output=True
    )
    if result.returncode == 0:
        print(f"    {YELLOW}No changes to commit{NC}")
        return True

    result = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"    {GREEN}Committed: {message}{NC}")
        return True
    else:
        print(f"    {RED}Commit failed: {result.stderr.strip()}{NC}")
        return False


def iter_workflows(config: dict):
    """Yield (name, path) for each configured workflow."""
    base = Path(config["workflows_dir"])
    for name in config["workflows"]:
        path = base / name
        if path.is_dir():
            yield name, path
        else:
            print(f"  {YELLOW}Warning: {path} does not exist, skipping{NC}")


# --- sync command ---


def collect_sync_files(ref_path: Path, config: dict) -> list[str]:
    """Collect all relative file paths to sync from the reference repo."""
    sync_dirs = config.get("sync_dirs", [])
    sync_files = config.get("sync_files", [])
    files = []
    for d in sync_dirs:
        dir_path = ref_path / d
        if dir_path.is_dir():
            for f in sorted(dir_path.rglob("*")):
                if f.is_file():
                    files.append(str(f.relative_to(ref_path)))
    for f in sync_files:
        if (ref_path / f).is_file():
            files.append(f)
    return files


def file_diff(src: Path, dst: Path, label: str) -> list[str]:
    """Return unified diff lines between two files."""
    if not dst.exists():
        return [f"+++ new file: {label}"]

    src_lines = src.read_text().splitlines(keepends=True)
    dst_lines = dst.read_text().splitlines(keepends=True)

    return list(unified_diff(dst_lines, src_lines, fromfile=f"a/{label}", tofile=f"b/{label}", n=1))


def cmd_sync(config: dict, dry_run: bool, commit: bool):
    ref_name = config["reference"]
    ref_path = Path(config["workflows_dir"]) / ref_name

    if not ref_path.is_dir():
        print(f"{RED}Reference repo not found: {ref_path}{NC}")
        sys.exit(1)

    sync_files = collect_sync_files(ref_path, config)
    print(f"{BOLD}Syncing {len(sync_files)} files from {ref_name}{NC}")
    print(f"  Files: {', '.join(sync_files)}\n")

    results = {"synced": [], "skipped": [], "failed": []}

    for name, wf_path in iter_workflows(config):
        if name == ref_name:
            continue

        print(f"{CYAN}━━━ {name} ━━━{NC}")
        changed = 0

        for rel in sync_files:
            src = ref_path / rel
            dst = wf_path / rel

            diff = file_diff(src, dst, rel)
            if not diff:
                continue

            changed += 1
            if dry_run:
                print(f"  {YELLOW}Would update:{NC} {rel}")
                for line in diff[:20]:
                    print(f"    {line.rstrip()}")
                if len(diff) > 20:
                    print(f"    ... ({len(diff) - 20} more lines)")
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"  {GREEN}Updated:{NC} {rel}")

        if changed == 0:
            print(f"  {GREEN}Already up to date{NC}")
            results["skipped"].append(name)
        else:
            results["synced"].append(name)

        if commit and not dry_run and changed > 0:
            git_commit(wf_path, "chore: sync shared files from reference repo")

        print()

    # Summary
    print(f"{BOLD}Summary:{NC}")
    if results["synced"]:
        verb = "Would sync" if dry_run else "Synced"
        print(f"  {GREEN}{verb}: {', '.join(results['synced'])}{NC}")
    if results["skipped"]:
        print(f"  {BLUE}Up to date: {', '.join(results['skipped'])}{NC}")


# --- bump command ---


def bump_pixi_toml(path: Path, bumps: dict[str, str], dry_run: bool) -> bool:
    """Bump dependency versions in pixi.toml. Returns True if changed."""
    if not path.exists():
        return False

    content = path.read_text()
    original = content

    for dep_key, new_version in bumps.items():
        dep_name = DEP_NAMES[dep_key]
        # Match: dep-name = "version-spec"
        pattern = re.compile(
            rf'^(\s*{re.escape(dep_name)}\s*=\s*")([^"]+)(")',
            re.MULTILINE,
        )
        match = pattern.search(content)
        if match:
            old = match.group(2)
            if old != new_version:
                print(f"    pixi.toml: {dep_name} {YELLOW}{old}{NC} -> {GREEN}{new_version}{NC}")
                if not dry_run:
                    content = pattern.sub(rf"\g<1>{new_version}\3", content)

    if content != original and not dry_run:
        path.write_text(content)
        return True
    return content != original


def bump_spec_yaml(path: Path, bumps: dict[str, str], dry_run: bool) -> bool:
    """Bump dependency versions in spec.yaml requirements block. Returns True if changed."""
    if not path.exists():
        return False

    lines = path.read_text().splitlines(keepends=True)
    changed = False
    i = 0

    while i < len(lines):
        # Look for "- name: <dep>" lines
        for dep_key, new_version in bumps.items():
            dep_name = DEP_NAMES[dep_key]
            name_pattern = rf"^\s*-\s*name:\s*{re.escape(dep_name)}\s*$"
            if re.match(name_pattern, lines[i]):
                # Next line should be "    version: ..."
                if i + 1 < len(lines):
                    ver_match = re.match(r'^(\s*version:\s*["\']?)([^"\']+)(["\']?\s*)$', lines[i + 1])
                    if ver_match:
                        old = ver_match.group(2)
                        if old != new_version:
                            print(f"    spec.yaml: {dep_name} {YELLOW}{old}{NC} -> {GREEN}{new_version}{NC}")
                            if not dry_run:
                                lines[i + 1] = f"{ver_match.group(1)}{new_version}{ver_match.group(3)}"
                            changed = True
        i += 1

    if changed and not dry_run:
        path.write_text("".join(lines))

    return changed


def cmd_bump(config: dict, bumps: dict[str, str], dry_run: bool, commit: bool):
    if not bumps:
        print(f"{RED}No versions specified. Use --core, --ext-ecoscope, or --ext-custom.{NC}")
        sys.exit(1)

    print(f"{BOLD}Bumping versions:{NC}")
    for dep_key, ver in bumps.items():
        print(f"  {DEP_NAMES[dep_key]}: {GREEN}{ver}{NC}")
    print()

    results = {"bumped": [], "unchanged": [], "failed": []}

    for name, wf_path in iter_workflows(config):
        print(f"{CYAN}━━━ {name} ━━━{NC}")

        pixi_changed = bump_pixi_toml(wf_path / "pixi.toml", bumps, dry_run)
        spec_changed = bump_spec_yaml(wf_path / "spec.yaml", bumps, dry_run)

        if pixi_changed or spec_changed:
            results["bumped"].append(name)
        else:
            print(f"    {GREEN}Already up to date{NC}")
            results["unchanged"].append(name)

        if commit and not dry_run and (pixi_changed or spec_changed):
            parts = [f"{DEP_NAMES[k]} {v}" for k, v in bumps.items()]
            git_commit(wf_path, f"chore: bump {', '.join(parts)}")

        print()

    # Summary
    print(f"{BOLD}Summary:{NC}")
    if results["bumped"]:
        verb = "Would bump" if dry_run else "Bumped"
        print(f"  {GREEN}{verb}: {', '.join(results['bumped'])}{NC}")
    if results["unchanged"]:
        print(f"  {BLUE}Unchanged: {', '.join(results['unchanged'])}{NC}")


# --- run command ---


def cmd_run(config: dict, command: list[str]):
    if not command:
        print(f"{RED}No command specified. Usage: batch-update.py run -- <command> [args...]{NC}")
        sys.exit(1)

    cmd_str = " ".join(command)
    print(f"{BOLD}Running in each repo:{NC} {cmd_str}\n")

    results = {"passed": [], "failed": []}

    for name, wf_path in iter_workflows(config):
        print(f"{CYAN}━━━ {name} ━━━{NC}")

        result = subprocess.run(
            command,
            cwd=wf_path,
            text=True,
        )

        if result.returncode == 0:
            print(f"  {GREEN}OK{NC}")
            results["passed"].append(name)
        else:
            print(f"  {RED}FAILED (exit {result.returncode}){NC}")
            results["failed"].append(name)

        print()

    # Summary
    print(f"{BOLD}Summary:{NC}")
    total = len(results["passed"]) + len(results["failed"])
    print(f"  Total: {total}, {GREEN}Passed: {len(results['passed'])}{NC}, {RED}Failed: {len(results['failed'])}{NC}")
    if results["failed"]:
        print(f"  {RED}Failed repos: {', '.join(results['failed'])}{NC}")
        sys.exit(1)


# --- status command ---


def cmd_status(config: dict):
    print(f"{BOLD}Workflow Status{NC}\n")

    for name, wf_path in iter_workflows(config):
        print(f"{CYAN}━━━ {name} ━━━{NC}")

        # Current branch + git status
        branch = get_git_branch(wf_path)
        if branch:
            color = YELLOW if branch != "main" else GREEN
            # Check for uncommitted changes
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=wf_path,
                capture_output=True,
                text=True,
            )
            dirty = status.stdout.strip()
            if dirty:
                file_count = len(dirty.splitlines())
                print(f"  Branch: {color}{branch}{NC} ({RED}{file_count} uncommitted{NC})")
                for line in dirty.splitlines()[:5]:
                    print(f"    {line}")
                if file_count > 5:
                    print(f"    ... ({file_count - 5} more)")
            else:
                print(f"  Branch: {color}{branch}{NC} ({GREEN}clean{NC})")
        else:
            print(f"  Branch: {RED}(not a git repo){NC}")

        # Open PRs
        result = subprocess.run(
            ["gh", "pr", "list", "--state", "open", "--json", "number,title,headRefName,url", "--limit", "10"],
            cwd=wf_path,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            prs = json.loads(result.stdout)
            if prs:
                for pr in prs:
                    print(f"  PR #{pr['number']}: {pr['title']}")
                    print(f"    {BLUE}{pr['url']}{NC}")
            else:
                print(f"  PRs: {YELLOW}none open{NC}")
        else:
            print(f"  PRs: {RED}gh cli error{NC}")

        print()


# --- forms command ---


def cmd_forms(config: dict):
    print(f"{BOLD}rjsf.json Paths{NC}\n")

    for name, wf_path in iter_workflows(config):
        rjsf_files = list(wf_path.glob("**/rjsf.json"))
        if rjsf_files:
            print(f"  {GREEN}{name}{NC}: {rjsf_files[0]}")
        else:
            print(f"  {YELLOW}{name}{NC}: not found")


# --- main ---


def main():
    parser = argparse.ArgumentParser(
        description="Batch update ecoscope workflow repositories.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG, help="Path to config YAML"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # sync
    sync_parser = subparsers.add_parser("sync", help="Sync shared files from reference repo")
    sync_parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    sync_parser.add_argument("--commit", action="store_true", help="Commit changes (refuses on main)")

    # bump
    bump_parser = subparsers.add_parser("bump", help="Bump dependency versions")
    bump_parser.add_argument("--core", metavar="VER", help="Version for ecoscope-workflows-core")
    bump_parser.add_argument("--ext-ecoscope", metavar="VER", help="Version for ecoscope-workflows-ext-ecoscope")
    bump_parser.add_argument("--ext-custom", metavar="VER", help="Version for ecoscope-workflows-ext-custom")
    bump_parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    bump_parser.add_argument("--commit", action="store_true", help="Commit changes (refuses on main)")

    # status
    subparsers.add_parser("status", help="Show current branch and open PRs")

    # forms
    subparsers.add_parser("forms", help="Show rjsf.json paths for all workflows")

    # run
    run_parser = subparsers.add_parser("run", help="Run a command in each repo")
    run_parser.add_argument("cmd", nargs=argparse.REMAINDER, help="Command to run (after --)")

    args = parser.parse_args()

    config = load_config(args.config)

    if args.command == "sync":
        cmd_sync(config, args.dry_run, args.commit)
    elif args.command == "bump":
        bumps = {}
        if args.core:
            bumps["core"] = args.core
        if args.ext_ecoscope:
            bumps["ext_ecoscope"] = args.ext_ecoscope
        if args.ext_custom:
            bumps["ext_custom"] = args.ext_custom
        cmd_bump(config, bumps, args.dry_run, args.commit)
    elif args.command == "status":
        cmd_status(config)
    elif args.command == "forms":
        cmd_forms(config)
    elif args.command == "run":
        # Strip leading "--" from remainder
        cmd = args.cmd
        if cmd and cmd[0] == "--":
            cmd = cmd[1:]
        cmd_run(config, cmd)


if __name__ == "__main__":
    main()
