from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..checks.base import CheckResult
from ..checks.disk import check_disk
from ..checks.docker import check_docker
from ..checks.ports import check_port_in_use


@dataclass(slots=True)
class RuleExecution:
    name: str
    check_type: str
    result: CheckResult


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

        result = _run_single_check(rule)
        results.append(result)

    return results