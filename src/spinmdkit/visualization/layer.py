"""Single-layer magnetic-moment rendering."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from spinmdkit.analysis import LayerSelection, moment_norms
from spinmdkit.data import Frame

DEFAULT_RASTER_DPI = 300


def render_spin_layer(
    frame: Frame,
    selection: LayerSelection,
    output: str | Path,
    *,
    arrow_scale: float = 1.0,
    point_size: float = 24.0,
    dpi: int = DEFAULT_RASTER_DPI,
    moment_unit: str = "source unit",
    position_unit: str = "source unit",
    cmap: str = "viridis",
    title: str | None = None,
) -> tuple[Path, Path, Path]:
    """Render selected moments to editable SVG, PDF, and preview PNG files."""

    if not np.isfinite(arrow_scale) or arrow_scale <= 0:
        raise ValueError("arrow_scale must be a finite positive number")
    if not np.isfinite(point_size) or point_size <= 0:
        raise ValueError("point_size must be a finite positive number")
    if dpi < 1:
        raise ValueError("dpi must be positive")
    if not moment_unit.strip() or not position_unit.strip():
        raise ValueError("moment and position units must not be empty")
    if np.any(selection.indices < 0) or np.any(selection.indices >= len(frame)):
        raise IndexError("layer selection contains an atom index outside the frame")

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib import colormaps
        from matplotlib import colors as mpl_colors
    except ImportError as exc:
        raise RuntimeError("plotting requires: pip install 'spinmdkit[plot]'") from exc

    positions = frame.positions[selection.indices]
    spins = frame.spins[selection.indices]
    magnitudes = moment_norms(spins)
    plane_axes = selection.in_plane_axes
    plane_labels = selection.in_plane_labels
    plane_positions = positions[:, plane_axes]
    plane_spins = spins[:, plane_axes]
    plane_magnitudes = np.linalg.norm(plane_spins, axis=1)
    magnitude_min = float(np.min(magnitudes))
    magnitude_max = float(np.max(magnitudes))
    color_map = colormaps.get_cmap(cmap)

    plane_magnitude_min = float(np.min(plane_magnitudes))
    plane_magnitude_max = float(np.max(plane_magnitudes))
    if np.isclose(plane_magnitude_min, plane_magnitude_max):
        plane_color_padding = max(abs(plane_magnitude_min) * 1e-6, 1e-12)
        plane_color_min = plane_magnitude_min - plane_color_padding
        plane_color_max = plane_magnitude_max + plane_color_padding
    else:
        plane_color_min = plane_magnitude_min
        plane_color_max = plane_magnitude_max
    plane_normalization = mpl_colors.Normalize(
        vmin=plane_color_min, vmax=plane_color_max
    )
    plane_arrow_colors = color_map(plane_normalization(plane_magnitudes))

    style = {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "font.size": 9,
    }
    with plt.rc_context(style):
        figure = plt.figure(figsize=(7.2, 4.2), constrained_layout=True)
        spatial_axis = figure.add_subplot(121, projection="3d")
        projection_axis = figure.add_subplot(122)
        spatial_axis.scatter(
            positions[:, 0],
            positions[:, 1],
            positions[:, 2],
            color="#355f8d",
            s=point_size,
            edgecolors="#303030",
            linewidths=0.45,
            depthshade=False,
            zorder=3,
        )
        spatial_axis.quiver(
            positions[:, 0],
            positions[:, 1],
            positions[:, 2],
            spins[:, 0],
            spins[:, 1],
            spins[:, 2],
            length=arrow_scale,
            normalize=False,
            color="#355f8d",
            linewidth=1.15,
            arrow_length_ratio=0.22,
        )

        tips = positions + spins * arrow_scale
        extent_points = np.vstack((positions, tips))
        lower = np.min(extent_points, axis=0)
        upper = np.max(extent_points, axis=0)
        spans = upper - lower
        largest_span = max(float(np.max(spans)), 1.0)
        display_spans = np.maximum(spans, largest_span * 0.35)
        centers = (lower + upper) / 2.0
        for setter, center, span in zip(
            (
                spatial_axis.set_xlim,
                spatial_axis.set_ylim,
                spatial_axis.set_zlim,
            ),
            centers,
            display_spans,
        ):
            half_span = float(span) * 0.58
            setter(float(center) - half_span, float(center) + half_span)
        spatial_axis.set_box_aspect(display_spans)
        spatial_axis.view_init(elev=27.0, azim=-58.0)
        spatial_axis.set_xlabel(f"x ({position_unit})", labelpad=-1)
        spatial_axis.set_ylabel(f"y ({position_unit})", labelpad=-1)
        spatial_axis.set_zlabel("z", labelpad=-8)
        spatial_axis.locator_params(nbins=4)
        spatial_axis.set_title("3D moments")
        spatial_axis.grid(True, color="#d8d8d8", linewidth=0.55, alpha=0.7)

        projection_axis.scatter(
            plane_positions[:, 0],
            plane_positions[:, 1],
            c=plane_arrow_colors,
            s=point_size,
            edgecolors="#303030",
            linewidths=0.45,
            zorder=3,
        )
        projection_axis.quiver(
            plane_positions[:, 0],
            plane_positions[:, 1],
            plane_spins[:, 0],
            plane_spins[:, 1],
            angles="xy",
            scale_units="xy",
            scale=1.0 / arrow_scale,
            color=plane_arrow_colors,
            width=0.008,
            headwidth=4.0,
            headlength=5.0,
            headaxislength=4.5,
            zorder=4,
        )
        plane_tips = plane_positions + plane_spins * arrow_scale
        plane_extent = np.vstack((plane_positions, plane_tips))
        plane_lower = np.min(plane_extent, axis=0)
        plane_upper = np.max(plane_extent, axis=0)
        plane_spans = plane_upper - plane_lower
        plane_padding = np.maximum(plane_spans * 0.10, 0.10)
        projection_axis.set_xlim(
            float(plane_lower[0] - plane_padding[0]),
            float(plane_upper[0] + plane_padding[0]),
        )
        projection_axis.set_ylim(
            float(plane_lower[1] - plane_padding[1]),
            float(plane_upper[1] + plane_padding[1]),
        )
        projection_axis.set_aspect("equal", adjustable="box")
        projection_axis.set_xlabel(f"{plane_labels[0]} ({position_unit})")
        projection_axis.set_ylabel(f"{plane_labels[1]} ({position_unit})")
        projection_axis.set_title(
            f"{selection.projection_name} projection | "
            f"m{plane_labels[0]}, m{plane_labels[1]} only"
        )
        projection_axis.grid(True, color="#d8d8d8", linewidth=0.55, alpha=0.7)

        figure.suptitle(
            title
            or (
                f"{selection.selection_label} | {selection.axis}-layer magnetic moments "
                f"| {len(selection)} atoms"
            ),
            fontweight="bold",
        )
        spatial_axis.text2D(
            0.02,
            0.97,
            (
                f"{selection.axis} = {selection.coordinate_min:.5g}.."
                f"{selection.coordinate_max:.5g} {position_unit}\n"
                f"Full |m| = {magnitude_min:.5g}–{magnitude_max:.5g} "
                f"{moment_unit}\n"
                f"Arrow scale = {arrow_scale:.5g} {position_unit}/{moment_unit}"
            ),
            transform=spatial_axis.transAxes,
            ha="left",
            va="top",
            fontsize=8,
            color="#303030",
        )

        scalar_map = matplotlib.cm.ScalarMappable(
            norm=plane_normalization, cmap=color_map
        )
        scalar_map.set_array(plane_magnitudes)
        colorbar = figure.colorbar(
            scalar_map,
            ax=projection_axis,
            location="right",
            shrink=0.82,
            pad=0.04,
        )
        colorbar.set_label(f"In-plane moment magnitude ({moment_unit})")
        colorbar.ax.set_title(
            f"Range\n{plane_magnitude_min:.5g}–{plane_magnitude_max:.5g}",
            fontsize=8,
            pad=8,
        )

        requested = Path(output)
        base = requested.with_suffix("") if requested.suffix else requested
        svg_target = base.with_suffix(".svg")
        pdf_target = base.with_suffix(".pdf")
        png_target = base.with_suffix(".png")
        svg_target.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(svg_target, bbox_inches="tight")
        figure.savefig(pdf_target, bbox_inches="tight")
        figure.savefig(png_target, dpi=dpi, bbox_inches="tight")
        plt.close(figure)
    return svg_target, pdf_target, png_target
