"""Format-neutral trajectory reader contracts."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol, TextIO

from spinmdkit.data import Frame

TrajectorySource = str | Path | TextIO


class TrajectoryReader(Protocol):
    """Contract implemented by every input-format adapter."""

    name: str
    extensions: tuple[str, ...]

    def iter_frames(self, source: TrajectorySource) -> Iterator[Frame]:
        """Yield validated, format-neutral frames from *source*."""
