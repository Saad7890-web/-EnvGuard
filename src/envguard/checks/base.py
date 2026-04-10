from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CheckResult:
    name: str
    passed: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    check_type: str = "unknown"