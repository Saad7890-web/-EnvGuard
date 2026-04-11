from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard",
        description="Self-healing dev environment doctor",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Workspace root directory (defaults to current directory).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase logging verbosity.",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Assume yes for fix actions.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without changing anything.",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="command")

    subparsers.add_parser("check", help="Run environment checks")
    subparsers.add_parser("fix", help="Run automatic fixes for failed checks")
    subparsers.add_parser("report", help="Show saved execution history")
    subparsers.add_parser("watch", help="Continuously monitor the environment")

    return parser