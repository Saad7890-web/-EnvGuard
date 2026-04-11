from __future__ import annotations

import logging
from datetime import datetime, timezone

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..cli import build_parser
from ..config import load_config
from ..core import run_checks
from ..core.engine import run_checks_and_fixes
from ..logger import setup_logging
from ..paths import ensure_runtime_files

console = Console()


def _print_check_results(results) -> int:
    table = Table(title="EnvGuard Check Results", show_lines=False)
    table.add_column("Status", style="bold")
    table.add_column("Check")
    table.add_column("Message")
    table.add_column("Details", overflow="fold")

    has_failures = False

    for result in results:
        status = "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]"
        if not result.passed:
            has_failures = True

        details_text = ", ".join(f"{k}={v}" for k, v in result.details.items()) if result.details else "-"
        table.add_row(status, result.name, result.message, details_text)

    console.print(table)
    return 1 if has_failures else 0


def _print_fix_results(results) -> int:
    table = Table(title="EnvGuard Fix Results", show_lines=False)
    table.add_column("Check")
    table.add_column("Check Status")
    table.add_column("Fix Status")
    table.add_column("Message")
    table.add_column("Details", overflow="fold")

    has_fix_failures = False

    for item in results:
        check_status = "[green]PASS[/green]" if item.check.passed else "[red]FAIL[/red]"
        if item.fix is None:
            fix_status = "-"
            fix_message = "No fix needed"
            details_text = ", ".join(f"{k}={v}" for k, v in item.check.details.items()) if item.check.details else "-"
        else:
            fix_status = "[green]OK[/green]" if item.fix.success else "[red]FAILED[/red]"
            fix_message = item.fix.message
            if not item.fix.success:
                has_fix_failures = True
            details_text = ", ".join(f"{k}={v}" for k, v in item.fix.details.items()) if item.fix.details else "-"

        table.add_row(item.check.name, check_status, fix_status, fix_message, details_text)

    console.print(table)
    return 1 if has_fix_failures else 0


def _print_bootstrap_info(command: str, workspace_root: str) -> int:
    console.print(
        Panel.fit(
            f"[bold green]EnvGuard[/bold green]\n\n"
            f"[bold]Command:[/bold] {command}\n"
            f"[bold]Workspace:[/bold] {workspace_root}\n"
            f"[bold]Time:[/bold] {datetime.now(timezone.utc).isoformat()}\n",
            title="EnvGuard",
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

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "check":
        rules = config.rules
        if not rules:
            console.print("[yellow]No checks found in configs/rules.yaml[/yellow]")
            return 0

        results = run_checks(rules)
        return _print_check_results(results)

    if args.command == "fix":
        rules = config.rules
        if not rules:
            console.print("[yellow]No checks found in configs/rules.yaml[/yellow]")
            return 0

        combined = run_checks_and_fixes(rules, dry_run=getattr(args, "dry_run", False))
        return _print_fix_results(combined)

    if args.command in {"report", "watch"}:
        return _print_bootstrap_info(args.command, str(paths.root))

    parser.print_help()
    return 0