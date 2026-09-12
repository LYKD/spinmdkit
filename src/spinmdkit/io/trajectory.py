"""Small trajectory access facade independent of analysis and plotting."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from spinmdkit.data import Frame

from .extxyz import iter_extxyz, read_frame


@dataclass(frozen=True, slots=True)
class Trajectory:
    """A reusable reference to a streamed Extended XYZ trajectory."""

    path: Path

    def __init__(self, path: str | Path):
        object.__setattr__(self, "path", Path(path))

    def __iter__(self):
        return iter_extxyz(self.path)

    def frame(self, index: int = 0) -> Frame:
        return read_frame(self.path, index)
