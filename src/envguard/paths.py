from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DEFAULT_RULES_YAML = """version: 1
checks: []
"""

DEFAULT_HISTORY_JSON = "[]\n"


@dataclass(frozen=True, slots=True)
class RuntimePaths:
    root: Path
    config_dir: Path
    reports_dir: Path
    rules_file: Path
    history_file: Path


def get_runtime_paths(root: Path | str | None = None) -> RuntimePaths:
    workspace_root = Path(root).expanduser().resolve() if root is not None else Path.cwd().resolve()
    config_dir = workspace_root / "configs"
    reports_dir = workspace_root / "reports"

    return RuntimePaths(
        root=workspace_root,
        config_dir=config_dir,
        reports_dir=reports_dir,
        rules_file=config_dir / "rules.yaml",
        history_file=reports_dir / "history.json",
    )


def ensure_runtime_files(root: Path | str | None = None) -> RuntimePaths:
    paths = get_runtime_paths(root)

    paths.config_dir.mkdir(parents=True, exist_ok=True)
    paths.reports_dir.mkdir(parents=True, exist_ok=True)

    if not paths.rules_file.exists():
        paths.rules_file.write_text(DEFAULT_RULES_YAML, encoding="utf-8")

    if not paths.history_file.exists():
        paths.history_file.write_text(DEFAULT_HISTORY_JSON, encoding="utf-8")

    return paths