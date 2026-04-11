from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..checks.base import CheckResult
from ..checks.disk import check_disk
from ..checks.docker import check_docker
from ..checks.ports import check_port_in_use
from ..fixes.base import FixResult
from ..fixes.disk import clean_temp
from ..fixes.docker import fix_docker
from ..fixes.ports import kill_port


@dataclass(slots=True)
class CheckAndFixResult:
    check: CheckResult
    fix: FixResult | None = None


def _run_single_check(rule: dict[str, Any]) -> CheckResult:
    check_type = str(rule.get("type", "")).strip().lower()
    name = str(rule.get("name", check_type or "unknown")).strip()

    if check_type == "docker":
        result = check_docker()
        result.name = name
        return result

    if check_type == "port":
        port = int(rule.get("port", 0))
        host = str(rule.get("host", "127.0.0.1"))
        result = check_port_in_use(port=port, host=host)
        result.name = name
        return result

    if check_type == "disk":
        path = str(rule.get("path", "/"))
        threshold_percent = int(rule.get("threshold_percent", 90))
        result = check_disk(path=path, threshold_percent=threshold_percent)
        result.name = name
        return result

    return CheckResult(
        name=name,
        passed=False,
        message=f"Unknown check type: {check_type}",
        details={"rule": rule},
        check_type=check_type or "unknown",
    )


def run_checks(rules: list[dict[str, Any]]) -> list[CheckResult]:
    results: list[CheckResult] = []

    for rule in rules:
        if not isinstance(rule, dict):
            results.append(
                CheckResult(
                    name="invalid_rule",
                    passed=False,
                    message="Rule must be a dictionary",
                    details={"rule": rule},
                    check_type="invalid",
                )
            )
            continue

        results.append(_run_single_check(rule))

    return results


def _run_single_fix(rule: dict[str, Any], check_result: CheckResult, dry_run: bool = False) -> FixResult:
    fix_name = str(rule.get("fix", "")).strip()
    check_type = str(rule.get("type", "")).strip().lower()

    if dry_run:
        return FixResult(
            name=fix_name or "dry_run",
            success=True,
            message="Dry run: fix skipped",
            details={"rule": rule, "check": check_result.name},
        )

    if fix_name == "fix_docker" and check_type == "docker":
        return fix_docker()

    if fix_name == "kill_port" and check_type == "port":
        port = int(rule.get("port", 0))
        return kill_port(port)

    if fix_name == "clean_temp" and check_type == "disk":
        return clean_temp()

    return FixResult(
        name=fix_name or "unknown_fix",
        success=False,
        message="No matching fix found for rule",
        details={"rule": rule, "check": check_result.name},
    )


def run_checks_and_fixes(
    rules: list[dict[str, Any]],
    *,
    dry_run: bool = False,
) -> list[CheckAndFixResult]:
    """
    Runs checks and automatically applies fixes when a check fails.
    """
    combined: list[CheckAndFixResult] = []
    checks = run_checks(rules)

    rule_by_name = {
        str(rule.get("name")): rule
        for rule in rules
        if isinstance(rule, dict) and rule.get("name")
    }

    for check_result in checks:
        rule = rule_by_name.get(check_result.name)

        if check_result.passed or not rule:
            combined.append(CheckAndFixResult(check=check_result, fix=None))
            continue

        fix_result = _run_single_fix(rule, check_result, dry_run=dry_run)
        combined.append(CheckAndFixResult(check=check_result, fix=fix_result))

    return combined