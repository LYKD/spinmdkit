"""Format-neutral magnetic-moment time-series analysis."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from numbers import Real

import numpy as np
from numpy.typing import NDArray

from spinmdkit.data import Frame

from .summary import summarize_frame


@dataclass(slots=True)
class MomentSeries:
    """Per-frame magnetic observables ready for export or plotting."""

    frame_indices: NDArray[np.int64]
    times: NDArray[np.float64]
    atom_counts: NDArray[np.int64]
    net_moments: NDArray[np.float64]
    net_moment_norms: NDArray[np.float64]
    mean_moment_norms: NDArray[np.float64]
    min_moment_norms: NDArray[np.float64]
    max_moment_norms: NDArray[np.float64]
    time_unit: str
    moment_unit: str
    selection_label: str

    def __post_init__(self) -> None:
        self.frame_indices = np.asarray(self.frame_indices, dtype=np.int64)
        self.times = np.asarray(self.times, dtype=np.float64)
        self.atom_counts = np.asarray(self.atom_counts, dtype=np.int64)
        self.net_moments = np.asarray(self.net_moments, dtype=np.float64)
        self.net_moment_norms = np.asarray(
            self.net_moment_norms, dtype=np.float64
        )
        self.mean_moment_norms = np.asarray(
            self.mean_moment_norms, dtype=np.float64
        )
        self.min_moment_norms = np.asarray(self.min_moment_norms, dtype=np.float64)
        self.max_moment_norms = np.asarray(self.max_moment_norms, dtype=np.float64)
        size = len(self.frame_indices)
        one_dimensional = (
            self.times,
            self.atom_counts,
            self.net_moment_norms,
            self.mean_moment_norms,
            self.min_moment_norms,
            self.max_moment_norms,
        )
        if any(values.shape != (size,) for values in one_dimensional):
            raise ValueError("moment-series scalar columns must have equal length")
        if self.net_moments.shape != (size, 3):
            raise ValueError("net_moments must have shape (number_of_frames, 3)")
        if not self.time_unit.strip() or not self.moment_unit.strip():
            raise ValueError("time and moment units must not be empty")

    def __len__(self) -> int:
        return len(self.frame_indices)


def _selection_label(species: str | Sequence[str] | None) -> str:
    if species is None:
        return "all species"
    names = [species] if isinstance(species, str) else list(species)
    return ", ".join(names)


def _metadata_time(
    frame: Frame,
    frame_index: int,
    *,
    key: str,
    scale: float,
    offset: float,
) -> float:
    raw_value = frame.metadata.get(key)
    if isinstance(raw_value, bool) or not isinstance(raw_value, Real):
        raise TypeError(
            f"frame {frame_index} has no numeric metadata time key {key!r}"
        )
    return offset + float(raw_value) * scale


def analyze_moment_series(
    frames: Iterable[Frame],
    species: str | Sequence[str] | None = None,
    *,
    timestep: float = 1.0,
    sample_every: int = 1,
    time_offset: float = 0.0,
    time_source: str = "computed",
    time_key: str = "Time",
    time_scale: float = 1.0,
    time_unit: str = "step",
    moment_unit: str = "source unit",
    frame_stride: int = 1,
    max_frames: int | None = None,
) -> MomentSeries:
    """Calculate net and local-moment evolution from any frame iterator.

    In ``computed`` mode, physical time is
    ``time_offset + frame_index * timestep * sample_every``. ``sample_every``
    is the number of integration steps between stored trajectory frames, while
    ``frame_stride`` controls optional post-processing downsampling.

    In ``metadata`` mode, physical time is
    ``time_offset + frame.metadata[time_key] * time_scale``.
    """

    if not np.isfinite(timestep) or timestep <= 0:
        raise ValueError("timestep must be a finite positive number")
    if sample_every < 1:
        raise ValueError("sample_every must be positive")
    if frame_stride < 1:
        raise ValueError("frame_stride must be positive")
    if max_frames is not None and max_frames < 1:
        raise ValueError("max_frames must be positive")
    if not np.isfinite(time_offset):
        raise ValueError("time_offset must be finite")
    if not np.isfinite(time_scale) or time_scale <= 0:
        raise ValueError("time_scale must be a finite positive number")
    if time_source not in {"computed", "metadata"}:
        raise ValueError("time_source must be 'computed' or 'metadata'")
    if not time_key:
        raise ValueError("time_key must not be empty")

    frame_indices: list[int] = []
    times: list[float] = []
    atom_counts: list[int] = []
    net_moments: list[list[float]] = []
    net_moment_norms: list[float] = []
    mean_moment_norms: list[float] = []
    min_moment_norms: list[float] = []
    max_moment_norms: list[float] = []

    for frame_index, frame in enumerate(frames):
        if frame_index % frame_stride:
            continue
        summary = summarize_frame(frame, species)
        if time_source == "metadata":
            time = _metadata_time(
                frame,
                frame_index,
                key=time_key,
                scale=time_scale,
                offset=time_offset,
            )
        else:
            time = time_offset + frame_index * timestep * sample_every
        frame_indices.append(frame_index)
        times.append(time)
        atom_counts.append(int(summary["atoms"]))
        net_moments.append(list(summary["magnetization"]))
        net_moment_norms.append(float(summary["magnetization_norm"]))
        mean_moment_norms.append(float(summary["mean_moment_norm"]))
        min_moment_norms.append(float(summary["min_moment_norm"]))
        max_moment_norms.append(float(summary["max_moment_norm"]))
        if max_frames is not None and len(frame_indices) >= max_frames:
            break

    if not frame_indices:
        raise ValueError("trajectory contains no analyzed frames")
    return MomentSeries(
        frame_indices=np.asarray(frame_indices, dtype=np.int64),
        times=np.asarray(times, dtype=np.float64),
        atom_counts=np.asarray(atom_counts, dtype=np.int64),
        net_moments=np.asarray(net_moments, dtype=np.float64),
        net_moment_norms=np.asarray(net_moment_norms, dtype=np.float64),
        mean_moment_norms=np.asarray(mean_moment_norms, dtype=np.float64),
        min_moment_norms=np.asarray(min_moment_norms, dtype=np.float64),
        max_moment_norms=np.asarray(max_moment_norms, dtype=np.float64),
        time_unit=time_unit,
        moment_unit=moment_unit,
        selection_label=_selection_label(species),
    )
