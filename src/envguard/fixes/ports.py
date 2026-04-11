from __future__ import annotations

import psutil

from .base import FixResult


def kill_port(port: int) -> FixResult:
    """
    Terminates processes listening on the given port.
    """
    killed: list[int] = []
    errors: list[str] = []

    try:
        for proc in psutil.process_iter(attrs=["pid", "name"]):
            try:
                connections = proc.connections(kind="inet")
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue

            for conn in connections:
                laddr = getattr(conn, "laddr", None)
                if not laddr:
                    continue

                if getattr(laddr, "port", None) != port:
                    continue

                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                    killed.append(proc.pid)
                except psutil.TimeoutExpired:
                    try:
                        proc.kill()
                        proc.wait(timeout=5)
                        killed.append(proc.pid)
                    except Exception as exc:
                        errors.append(f"pid={proc.pid}: {exc}")
                except Exception as exc:
                    errors.append(f"pid={proc.pid}: {exc}")

        if killed:
            return FixResult(
                name=f"kill_port_{port}",
                success=True,
                message=f"Stopped process(es) using port {port}",
                details={"port": port, "killed_pids": killed, "errors": errors},
            )

        return FixResult(
            name=f"kill_port_{port}",
            success=False,
            message=f"No process found on port {port}",
            details={"port": port},
        )

    except Exception as exc:
        return FixResult(
            name=f"kill_port_{port}",
            success=False,
            message="Failed to inspect or kill port process",
            details={"port": port, "error": str(exc)},
        )