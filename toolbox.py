#!/usr/bin/env python3
"""Offline, cross-platform everyday command-line tools."""

from __future__ import annotations

import argparse
import json
import secrets
import shutil
import string
import sys
from pathlib import Path


def format_bytes(value: int) -> str:
    size = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB", "PiB"):
        if size < 1024 or unit == "PiB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PiB"


def disk_report(path: Path) -> dict[str, int | str]:
    target = path.expanduser().resolve()
    if not target.exists():
        raise FileNotFoundError(f"Path does not exist: {target}")
    usage = shutil.disk_usage(target)
    return {
        "path": str(target),
        "total_bytes": usage.total,
        "used_bytes": usage.used,
        "free_bytes": usage.free,
    }


def organize_folder(folder: Path, apply: bool = False) -> list[tuple[Path, Path]]:
    source = folder.expanduser().resolve()
    if not source.is_dir():
        raise NotADirectoryError(f"Not a directory: {source}")

    operations: list[tuple[Path, Path]] = []
    for item in sorted(source.iterdir(), key=lambda p: p.name.casefold()):
        if not item.is_file() or item.is_symlink():
            continue
        suffix = item.suffix.lower().lstrip(".")
        category = suffix if suffix and suffix.isalnum() else "no-extension"
        destination_dir = source / category
        destination = destination_dir / item.name
        if destination.exists():
            stem, ext = item.stem, item.suffix
            number = 2
            while (destination_dir / f"{stem} ({number}){ext}").exists():
                number += 1
            destination = destination_dir / f"{stem} ({number}){ext}"
        operations.append((item, destination))

    if apply:
        for old, new in operations:
            new.parent.mkdir(exist_ok=True)
            shutil.move(str(old), str(new))
    return operations


def make_password(length: int, use_symbols: bool = True) -> str:
    if length < 8 or length > 256:
        raise ValueError("Password length must be between 8 and 256 characters.")
    alphabet = string.ascii_letters + string.digits
    if use_symbols:
        alphabet += "!@#$%^&*()-_=+[]{}?"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="toolbox",
        description="Handy offline utilities for Windows, macOS, and Linux.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    organize = commands.add_parser("organize", help="Sort files into extension folders")
    organize.add_argument("folder", nargs="?", type=Path, default=Path.home() / "Downloads")
    organize.add_argument("--apply", action="store_true", help="Move files (default is preview only)")

    password = commands.add_parser("password", help="Generate a password locally")
    password.add_argument("--length", type=int, default=20)
    password.add_argument("--no-symbols", action="store_true")

    disk = commands.add_parser("disk", help="Show disk capacity for a path")
    disk.add_argument("path", nargs="?", type=Path, default=Path.home())
    disk.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "organize":
            operations = organize_folder(args.folder, apply=args.apply)
            if not operations:
                print("No files to organize.")
            for old, new in operations:
                prefix = "Moved" if args.apply else "Would move"
                print(f"{prefix}: {old.name} -> {new.parent.name}/{new.name}")
            if not args.apply and operations:
                print("Preview only. Add --apply to move these files.")
        elif args.command == "password":
            print(make_password(args.length, use_symbols=not args.no_symbols))
        elif args.command == "disk":
            report = disk_report(args.path)
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                print(f"Path:  {report['path']}")
                print(f"Total: {format_bytes(int(report['total_bytes']))}")
                print(f"Used:  {format_bytes(int(report['used_bytes']))}")
                print(f"Free:  {format_bytes(int(report['free_bytes']))}")
        return 0
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
