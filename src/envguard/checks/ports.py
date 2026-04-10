from __future__ import annotations

import socket

from .base import CheckResult


def check_port_in_use(port: int, host: str = "127.0.0.1") -> CheckResult:
    """
    Returns a failed check when the port is already occupied.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1.0)
        in_use = sock.connect_ex((host, port)) == 0

    if in_use:
        return CheckResult(
            name=f"port_{port}",
            passed=False,
            message=f"Port {port} is already in use",
            details={"host": host, "port": port},
            check_type="port",
        )

    return CheckResult(
        name=f"port_{port}",
        passed=True,
        message=f"Port {port} is free",
        details={"host": host, "port": port},
        check_type="port",
    )