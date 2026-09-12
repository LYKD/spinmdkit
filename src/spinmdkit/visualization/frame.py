"""Static frame rendering; Matplotlib is imported only on demand."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from spinmdkit.data import Frame


def render_spin_frame(
    frame: Frame,
    output: str | Path,
    *,
    species: str | list[str] | None = None,
    max_atoms: int = 4000,
    arrow_length: float = 1.0,
    point_size: float = 8.0,
    dpi: int = 180,
    normalize: bool = False,
    title: str | None = None,
) -> Path:
    """Render one 3D spin field to an image file."""

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("plotting requires: pip install 'spinmdkit[plot]'") from exc

    mask = frame.species_mask(species)
    if not np.any(mask):
        raise ValueError(f"no atoms match species selection {species!r}")
    positions = frame.positions[mask]
    spins = frame.spins[mask]
    selected_species = frame.species[mask]
    if max_atoms and len(positions) > max_atoms:
        indices = np.linspace(0, len(positions) - 1, max_atoms, dtype=int)
        positions = positions[indices]
        spins = spins[indices]
        selected_species = selected_species[indices]

    figure = plt.figure(figsize=(9, 7), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    color_values = spins[:, 2]
    limit = max(float(np.max(np.abs(color_values))), 1e-12)
    colors = plt.get_cmap("coolwarm")((color_values + limit) / (2.0 * limit))
    axis.scatter(
        positions[:, 0],
        positions[:, 1],
        positions[:, 2],
        c=colors,
        s=point_size,
        alpha=0.75,
    )
    axis.quiver(
        positions[:, 0],
        positions[:, 1],
        positions[:, 2],
        spins[:, 0],
        spins[:, 1],
        spins[:, 2],
        length=arrow_length,
        normalize=normalize,
        color=colors,
        linewidth=0.7,
    )
    ranges = np.ptp(positions, axis=0)
    center = np.mean([np.min(positions, axis=0), np.max(positions, axis=0)], axis=0)
    radius = max(float(np.max(ranges)) / 2.0, 0.5)
    axis.set_xlim(center[0] - radius, center[0] + radius)
    axis.set_ylim(center[1] - radius, center[1] + radius)
    axis.set_zlim(center[2] - radius, center[2] + radius)
    axis.set_xlabel("x")
    axis.set_ylabel("y")
    axis.set_zlabel("z")
    chosen = ", ".join(sorted(set(selected_species.tolist())))
    axis.set_title(title or f"SpinMDKit | {chosen} | {len(positions)} arrows")
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(target, dpi=dpi)
    plt.close(figure)
    return target
