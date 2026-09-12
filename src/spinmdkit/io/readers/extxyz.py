"""Extended XYZ adapter for the format-neutral reader registry."""

from __future__ import annotations

from collections.abc import Iterator

from spinmdkit.data import Frame
from spinmdkit.io.base import TrajectorySource
from spinmdkit.io.extxyz import iter_extxyz


class ExtXYZReader:
    """Read Extended XYZ, including current GPUMD/NEP-spin trajectories."""

    name = "extxyz"
    extensions = (".xyz", ".extxyz", ".xyz.gz", ".extxyz.gz")

    def iter_frames(self, source: TrajectorySource) -> Iterator[Frame]:
        return iter_extxyz(source)
