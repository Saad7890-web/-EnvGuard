from __future__ import annotations

import logging

from rich.console import Console
from rich.panel import Panel

from ..cli import build_parser
from ..config import load_config
from ..logger import setup_logging
from ..paths import ensure_runtime_files

console = Console()


def _render_phase_one_banner(command: str, workspace_root: str) -> int:
    console.print(
        Panel.fit(
            f"[bold green]EnvGuard[/bold green]\n\n"
            f"[bold]Command:[/bold] {command}\n"
            f"[bold]Workspace:[/bold] {workspace_root}\n\n"
            "Phase 1 is ready.\n"
            "The CLI boots correctly, config files are created, and logging is wired.\n"
            "Real checks and fixes will be added in later phases.",
            title="Bootstrapped",
        )
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    setup_logging(verbose=args.verbose > 0)

    paths = ensure_runtime_files(args.root)
    config = load_config(args.root)

    logger = logging.getLogger("envguard")
    logger.debug("Loaded config from %s", paths.rules_file)
    logger.debug("Loaded history file from %s", paths.history_file)
    logger.debug("Rule entries found: %d", len(config.rules))

    if not args.command:
        parser.print_help()
        return 0

    if args.command in {"check", "fix", "report", "watch"}:
        return _render_phase_one_banner(args.command, str(paths.root))

    parser.print_help()
    return 0