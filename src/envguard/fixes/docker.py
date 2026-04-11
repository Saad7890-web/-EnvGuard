from __future__ import annotations

import platform
import subprocess

from .base import FixResult


def _run_command(command: list[str]) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = (completed.stdout or completed.stderr or "").strip()
        return True, output
    except FileNotFoundError:
        return False, "command not found"
    except subprocess.TimeoutExpired:
        return False, "command timed out"
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        return False, stderr or f"exit code {exc.returncode}"


def fix_docker() -> FixResult:
    system = platform.system().lower()

    if system == "linux":
        for cmd in (
            ["systemctl", "start", "docker"],
            ["service", "docker", "start"],
        ):
            ok, output = _run_command(cmd)
            if ok:
                return FixResult(
                    name="fix_docker",
                    success=True,
                    message="Docker service started",
                    details={"command": " ".join(cmd), "output": output},
                )

        return FixResult(
            name="fix_docker",
            success=False,
            message="Could not start Docker on Linux",
            details={"attempts": ["systemctl start docker", "service docker start"]},
        )

    if system == "darwin":
        ok, output = _run_command(["open", "-a", "Docker"])
        if ok:
            return FixResult(
                name="fix_docker",
                success=True,
                message="Docker Desktop launch requested",
                details={"command": "open -a Docker", "output": output},
            )
        return FixResult(
            name="fix_docker",
            success=False,
            message="Could not launch Docker Desktop",
            details={"error": output},
        )

    if system == "windows":
        ok, output = _run_command(
            [
                "powershell",
                "-Command",
                "Start-Service docker",
            ]
        )
        if ok:
            return FixResult(
                name="fix_docker",
                success=True,
                message="Docker service started",
                details={"command": "powershell Start-Service docker", "output": output},
            )
        return FixResult(
            name="fix_docker",
            success=False,
            message="Could not start Docker on Windows",
            details={"error": output},
        )

    return FixResult(
        name="fix_docker",
        success=False,
        message=f"Unsupported platform for Docker fix: {system}",
        details={"platform": system},
    )