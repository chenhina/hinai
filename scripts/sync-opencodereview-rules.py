#!/usr/bin/env python3
"""Generate or check a repository's OpenCodeReview rule routing."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath


RULE_FILE = Path(".opencodereview/rule.json")
GUIDE_PRIORITY = {"AGENTS.md": 0, "CLAUDE.md": 1}
SKIP_DIRS = frozenset({".agents", ".claude", ".venv", "__pycache__", "node_modules", "vendor"})


def git(*args: str, cwd: Path | None = None) -> bytes:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, check=False)
    if result.returncode:
        message = result.stderr.decode(errors="replace").strip()
        raise RuntimeError(message or f"git {args[0]} failed")
    return result.stdout


def relative_directory(value: str) -> PurePosixPath:
    directory = PurePosixPath(value)
    if not directory.parts or directory.is_absolute() or ".." in directory.parts or "\\" in value:
        raise argparse.ArgumentTypeError("expected a repository-relative directory using '/'")
    return directory


def build_rules(root: Path, skip: list[PurePosixPath]) -> list[dict[str, str | bool]]:
    pathspecs = [f":(glob)**/{name}" for name in GUIDE_PRIORITY]
    paths = git("ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", *pathspecs, cwd=root)
    guides: dict[PurePosixPath, PurePosixPath] = {}
    for name in set(paths.split(b"\x00")) - {b""}:
        candidate = PurePosixPath(os.fsdecode(name))
        directory = candidate.parent
        if SKIP_DIRS.intersection(directory.parts) or any(directory.is_relative_to(prefix) for prefix in skip):
            continue

        file = root / candidate
        if not file.is_file():
            continue
        if not file.resolve().is_relative_to(root):
            raise ValueError(f"rule document points outside the repository: {candidate}")

        current = guides.get(directory)
        if current is None or GUIDE_PRIORITY[candidate.name] < GUIDE_PRIORITY[current.name]:
            guides[directory] = candidate

    if not guides:
        raise ValueError("no AGENTS.md or CLAUDE.md files found")

    rules: list[dict[str, str | bool]] = []
    scopes: set[str] = set()
    for directory in sorted(guides, key=lambda path: (-len(path.parts), path.as_posix())):
        module = directory.as_posix()
        if any(character in module for character in r"\*?[]{}"):
            raise ValueError(f"module path contains glob metacharacters: {module}")
        pattern = f"{module}/**" if directory.parts else "**/*"
        if pattern.lower() in scopes:
            raise ValueError(f"module paths conflict under case-insensitive matching: {module}")
        scopes.add(pattern.lower())
        rules.append({"path": pattern, "merge_system_rule": True, "rule": guides[directory].as_posix()})
    return rules


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key in existing rule.json")
        result[key] = value
    return result


def invalid_constant(value: str) -> None:
    raise ValueError(f"invalid JSON constant in existing rule.json: {value}")


def load_config(file: Path) -> dict[str, object]:
    if file.is_symlink() or file.parent.is_symlink():
        raise ValueError(f"{RULE_FILE} and its parent must be ordinary repository paths")
    if not file.exists():
        return {}
    config = json.loads(file.read_text(encoding="utf-8"), object_pairs_hook=unique_object, parse_constant=invalid_constant)
    if not isinstance(config, dict):
        raise ValueError(f"{RULE_FILE} must contain a JSON object")
    return config


def sync(args: argparse.Namespace) -> int:
    root = Path(os.fsdecode(git("rev-parse", "--show-toplevel").removesuffix(b"\n"))).resolve()
    file = root / RULE_FILE
    config = load_config(file)
    rules = build_rules(root, args.skip_dir)

    if json.dumps(config.get("rules"), sort_keys=True) == json.dumps(rules, sort_keys=True):
        print(f"{RULE_FILE} is up to date.")
        return 0
    if args.check:
        print(f"{RULE_FILE} is missing or out of sync. Run again with --write.", file=sys.stderr)
        return 1

    config["rules"] = rules
    content = json.dumps(config, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    file.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=file.parent) as temporary_dir:
        temporary_file = Path(temporary_dir) / file.name
        temporary_file.write_text(content, encoding="utf-8")
        temporary_file.replace(file)
    print(f"Updated {RULE_FILE} with {len(rules)} route(s).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="regenerate rules in the project config")
    mode.add_argument("--check", action="store_true", help="check for drift without writing")
    parser.add_argument(
        "--skip-dir", action="append", default=[], type=relative_directory, metavar="DIR",
        help="skip guide discovery under this repository-relative directory (repeatable)",
    )
    try:
        return sync(parser.parse_args())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Cannot sync OpenCodeReview rules: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
