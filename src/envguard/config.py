from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .paths import RuntimePaths, ensure_runtime_files


@dataclass(frozen=True, slots=True)
class AppConfig:
    paths: RuntimePaths
    raw: dict[str, Any]

    @property
    def rules(self) -> list[dict[str, Any]]:
        checks = self.raw.get("checks", [])
        return checks if isinstance(checks, list) else []


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {path}: {exc}") from exc

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping at the top level.")

    return data


def load_config(root: Path | str | None = None) -> AppConfig:
    paths = ensure_runtime_files(root)
    raw = _read_yaml(paths.rules_file)
    return AppConfig(paths=paths, raw=raw)