#!/usr/bin/env python3
"""Check selected text, JSON, and path rules against Git snapshots."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import PurePosixPath


TEXT_SUFFIXES = frozenset(
    """
    .c .conf .cpp .css .csv .go .h .html .java .js .json .jsonc .jsx
    .md .mdx .mjs .py .rs .sh .sql .toml .ts .tsx .txt .vue .xml .yaml .yml
    """.split()
)
TEXT_NAMES = frozenset(
    {".editorconfig", ".gitattributes", ".gitignore", "Dockerfile", "Makefile", "go.mod", "go.sum"}
)
ASCII_PATH = re.compile(r"[A-Za-z0-9._/-]+")


def git(*args: str, cwd: str | None = None) -> bytes:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, check=False)
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(message or f"git {args[0]} failed (exit {result.returncode})")
    return result.stdout


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    obj: dict[str, object] = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate object key")
        obj[key] = value
    return obj


def reject_json_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value}")


def check_text(path: PurePosixPath, contents: bytes) -> list[tuple[int | None, str, str]]:
    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError:
        return [(None, "TEXT001", "expected UTF-8 text")]

    issues: list[tuple[int | None, str, str]] = []
    lines = text.split("\n")
    if text and not text.endswith("\n"):
        issues.append((len(lines), "TEXT002", "missing final newline"))

    for line_number, raw_line in enumerate(lines, 1):
        line = raw_line.removesuffix("\r")
        trimmed = line.rstrip(" \t")
        if line == trimmed or (path.suffix.lower() == ".md" and trimmed and line == trimmed + "  "):
            continue
        issues.append((line_number, "TEXT003", "trailing spaces or tabs"))

    if path.suffix.lower() == ".json":
        try:
            json.loads(
                text,
                object_pairs_hook=unique_object,
                parse_constant=reject_json_constant,
                parse_int=str,
                parse_float=str,
            )
        except json.JSONDecodeError as error:
            issues.append((error.lineno, "JSON001", error.msg))
        except ValueError as error:
            issues.append((None, "JSON001", str(error)))
        except RecursionError:
            issues.append((None, "JSON001", "JSON nesting exceeds the parser limit"))

    return issues


def run(args: argparse.Namespace) -> int:
    root = os.fsdecode(git("rev-parse", "--show-toplevel").removesuffix(b"\n"))
    scope = ["--cached"]
    if args.base is not None:
        base = git("rev-parse", "--verify", "--end-of-options", f"{args.base}^{{commit}}", cwd=root)
        head = git("rev-parse", "--verify", "HEAD^{commit}", cwd=root)
        base_id, head_id = base.strip().decode("ascii"), head.strip().decode("ascii")
        merge_base = git("merge-base", base_id, head_id, cwd=root).strip().decode("ascii")
        scope = [merge_base, head_id]

    entries = git(
        "diff", "--raw", "-z", "--no-abbrev", "--no-renames", "--no-ext-diff",
        "--diff-filter=AMTU", *scope, "--", cwd=root,
    ).split(b"\x00")
    issue_count = 0
    for metadata, raw_path in zip(entries[0::2], entries[1::2]):
        _, mode, _, object_id, status = metadata.split()
        name = os.fsdecode(raw_path)
        if status == b"U":
            raise RuntimeError(f"unmerged index entry {name!r}")
        if args.ascii_paths and not ASCII_PATH.fullmatch(name):
            print(f"{name!r}: PATH001 use ASCII letters, digits, dots, underscores and hyphens")
            issue_count += 1

        path = PurePosixPath(name)
        if not mode.startswith(b"100") or (
            path.suffix.lower() not in TEXT_SUFFIXES and path.name not in TEXT_NAMES
        ):
            continue
        contents = git("cat-file", "blob", object_id.decode("ascii"), cwd=root)
        for line, rule, message in check_text(path, contents):
            location = f"{name!r}:{line}" if line is not None else repr(name)
            print(f"{location}: {rule} {message}")
            issue_count += 1

    if issue_count:
        print(f"{issue_count} policy issue(s) found.")
        return 1
    print("Repository policy checks passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--staged", action="store_true", help="check the Git index")
    scope.add_argument("--base", metavar="REF", help="check HEAD changes since its merge base with REF")
    parser.add_argument("--ascii-paths", action="store_true", help="also check changed paths")
    try:
        return run(parser.parse_args())
    except (OSError, RuntimeError) as error:
        print(f"Cannot check repository policy: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
