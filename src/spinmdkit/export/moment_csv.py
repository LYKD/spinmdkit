"""CSV serialization for magnetic-moment time series."""

from __future__ import annotations

import csv
from pathlib import Path

from spinmdkit.analysis import MomentSeries


def _number(value: float) -> str:
    return format(float(value), ".15g")


def write_moment_series_csv(
    series: MomentSeries, output: str | Path
) -> Path:
    """Write a self-describing, analysis-ready moment time series."""

    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "frame",
        "time",
        "time_unit",
        "atoms",
        "net_moment_x",
        "net_moment_y",
        "net_moment_z",
        "net_moment_norm",
        "mean_moment_norm",
        "min_moment_norm",
        "max_moment_norm",
        "moment_unit",
    ]
    with target.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for index in range(len(series)):
            writer.writerow(
                {
                    "frame": int(series.frame_indices[index]),
                    "time": _number(series.times[index]),
                    "time_unit": series.time_unit,
                    "atoms": int(series.atom_counts[index]),
                    "net_moment_x": _number(series.net_moments[index, 0]),
                    "net_moment_y": _number(series.net_moments[index, 1]),
                    "net_moment_z": _number(series.net_moments[index, 2]),
                    "net_moment_norm": _number(series.net_moment_norms[index]),
                    "mean_moment_norm": _number(series.mean_moment_norms[index]),
                    "min_moment_norm": _number(series.min_moment_norms[index]),
                    "max_moment_norm": _number(series.max_moment_norms[index]),
                    "moment_unit": series.moment_unit,
                }
            )
    return target
