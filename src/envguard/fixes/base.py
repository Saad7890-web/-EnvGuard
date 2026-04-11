from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class FixResult:
    name: str
    success: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)