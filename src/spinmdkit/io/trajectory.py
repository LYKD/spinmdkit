"""Small trajectory access facade independent of analysis and plotting."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from spinmdkit.data import Frame

from .registry import iter_frames, read_frame, resolve_reader


@dataclass(frozen=True, slots=True)
class Trajectory:
    """A reusable, format-neutral reference to a streamed trajectory."""

    path: Path
    format_name: str | None

    def __init__(self, path: str | Path, format_name: str | None = None):
        object.__setattr__(self, "path", Path(path))
        object.__setattr__(self, "format_name", format_name)

    def __iter__(self):
        return iter_frames(self.path, self.format_name)

    def frame(self, index: int = 0) -> Frame:
        return read_frame(self.path, index, self.format_name)

    @property
    def resolved_format(self) -> str:
        """Return the canonical name selected for this trajectory."""

        return resolve_reader(self.path, self.format_name).name
