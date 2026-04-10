from __future__ import annotations

import logging

from rich.logging import RichHandler


def setup_logging(verbose: bool = False) -> logging.Logger:
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                show_time=False,
                show_path=False,
            )
        ],
        force=True,
    )

    return logging.getLogger("envguard")