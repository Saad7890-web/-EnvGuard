from __future__ import annotations

import os
import shutil
import tempfile
import time
from pathlib import Path

from .base import FixResult


def clean_temp(max_age_hours: int = 24) -> FixResult:
    """
    Safely removes old files from the system temp directory.
    It avoids deleting the temp root itself and skips symlinks.
    """
    temp_dir = Path(tempfile.gettempdir())
    cutoff = time.time() - (max_age_hours * 3600)

    removed_files = 0
    removed_dirs = 0
    errors: list[str] = []

    try:
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            root_path = Path(root)

            for file_name in files:
                file_path = root_path / file_name

                try:
                    if file_path.is_symlink():
                        continue

                    stat = file_path.stat()
                    if stat.st_mtime < cutoff:
                        file_path.unlink(missing_ok=True)
                        removed_files += 1
                except Exception as exc:
                    errors.append(f"{file_path}: {exc}")

            for dir_name in dirs:
                dir_path = root_path / dir_name
                try:
                    if dir_path.is_symlink():
                        continue

                  
                    if dir_path.exists() and not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        removed_dirs += 1
                except Exception as exc:
                    errors.append(f"{dir_path}: {exc}")

        if removed_files or removed_dirs:
            return FixResult(
                name="clean_temp",
                success=True,
                message="Temporary files cleaned",
                details={
                    "temp_dir": str(temp_dir),
                    "removed_files": removed_files,
                    "removed_dirs": removed_dirs,
                    "errors": errors,
                },
            )

        return FixResult(
            name="clean_temp",
            success=True,
            message="Nothing to clean in temp directory",
            details={"temp_dir": str(temp_dir)},
        )

    except Exception as exc:
        return FixResult(
            name="clean_temp",
            success=False,
            message="Temp cleanup failed",
            details={"temp_dir": str(temp_dir), "error": str(exc)},
        )