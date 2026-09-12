"""Two-panel rendering for magnetic-moment time evolution."""

from __future__ import annotations

from pathlib import Path

from spinmdkit.analysis import MomentSeries


def render_moment_series(
    series: MomentSeries,
    output: str | Path,
    *,
    dpi: int = 180,
    title: str | None = None,
) -> Path:
    """Render net-vector and local-magnitude evolution side by side."""

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("plotting requires: pip install 'spinmdkit[plot]'") from exc

    if dpi < 1:
        raise ValueError("dpi must be positive")
    figure, axes = plt.subplots(1, 2, figsize=(13.0, 4.8), constrained_layout=True)
    left, right = axes
    time = series.times

    left.plot(time, series.net_moments[:, 0], label="Mx", color="#3977b7")
    left.plot(time, series.net_moments[:, 1], label="My", color="#d95f70")
    left.plot(time, series.net_moments[:, 2], label="Mz", color="#27823b")
    left.plot(time, series.net_moment_norms, label="|M|", color="#222222")
    left.axhline(0.0, color="#777777", linewidth=0.7, alpha=0.55)
    left.set_title("(a) Net magnetic moment", loc="left", fontweight="bold")
    left.set_ylabel(f"Net moment ({series.moment_unit})")
    left.legend(ncol=4, frameon=True, loc="best")

    right.plot(
        time,
        series.min_moment_norms,
        label="Minimum",
        color="#3977b7",
    )
    right.plot(
        time,
        series.mean_moment_norms,
        label="Mean",
        color="#e1812c",
    )
    right.plot(
        time,
        series.max_moment_norms,
        label="Maximum",
        color="#27823b",
    )
    right.set_title("(b) Local moment magnitude", loc="left", fontweight="bold")
    right.set_ylabel(f"Local moment magnitude ({series.moment_unit})")
    right.legend(ncol=3, frameon=True, loc="best")

    for axis in axes:
        axis.set_xlabel(f"Time ({series.time_unit})")
        axis.grid(axis="y", color="#d9d9d9", linewidth=0.8)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.margins(x=0.02)

    figure.suptitle(
        title or f"Magnetic-moment evolution | {series.selection_label}",
        fontweight="bold",
    )
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(target, dpi=dpi)
    plt.close(figure)
    return target
