from __future__ import annotations

import subprocess

from .base import CheckResult


def check_docker() -> CheckResult:
    """
    Checks whether Docker is available and responsive.
    """
    try:
        completed = subprocess.run(
            ["docker", "info"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = (completed.stdout or "").strip()
        return CheckResult(
            name="docker",
            passed=True,
            message="Docker is running",
            details={
                "source": "docker info",
                "output": output[:300] if output else "",
            },
            check_type="docker",
        )
    except FileNotFoundError:
        return CheckResult(
            name="docker",
            passed=False,
            message="Docker CLI is not installed",
            details={"error": "docker command not found"},
            check_type="docker",
        )
    except subprocess.TimeoutExpired:
        return CheckResult(
            name="docker",
            passed=False,
            message="Docker did not respond in time",
            details={"error": "timeout"},
            check_type="docker",
        )
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        return CheckResult(
            name="docker",
            passed=False,
            message="Docker is installed but not running",
            details={
                "returncode": exc.returncode,
                "stderr": stderr[:300],
            },
            check_type="docker",
        )