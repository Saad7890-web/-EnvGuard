from __future__ import annotations

from pathlib import Path
import shutil

from .base import CheckResult


def _get_usage_percent(path: str) -> float:
    usage = shutil.disk_usage(Path(path))
    return round((usage.used / usage.total) * 100, 2)


def check_disk(path: str = "/", threshold_percent: int = 90) -> CheckResult:
    """
    Checks whether disk usage is above a configured threshold.
    """
    try:
        percent = _get_usage_percent(path)
        passed = percent < threshold_percent

        if passed:
            return CheckResult(
                name=f"disk_{path}",
                passed=True,
                message=f"Disk usage is healthy: {percent}%",
                details={
                    "path": path,
                    "usage_percent": percent,
                    "threshold_percent": threshold_percent,
                },
                check_type="disk",
            )

        return CheckResult(
            name=f"disk_{path}",
            passed=False,
            message=f"Disk usage is high: {percent}%",
            details={
                "path": path,
                "usage_percent": percent,
                "threshold_percent": threshold_percent,
            },
            check_type="disk",
        )
    except Exception as exc:
        return CheckResult(
            name=f"disk_{path}",
            passed=False,
            message="Disk check failed",
            details={"path": path, "error": str(exc)},
            check_type="disk",
        )