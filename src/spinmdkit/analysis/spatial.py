"""Format-neutral spatial selections for atomistic frames."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from spinmdkit.data import Frame

_AXES = {"x": 0, "y": 1, "z": 2}
_LAYERS = {"top": "max", "max": "max", "bottom": "min", "min": "min"}


@dataclass(slots=True)
class LayerSelection:
    """Indices and coordinate bounds for one selected atomic layer."""

    indices: NDArray[np.int64]
    axis: str
    mode: str
    reference_coordinate: float
    coordinate_min: float
    coordinate_max: float
    tolerance: float | None
    selection_label: str

    def __post_init__(self) -> None:
        self.indices = np.asarray(self.indices, dtype=np.int64)
        if self.indices.ndim != 1 or self.indices.size == 0:
            raise ValueError("layer selection must contain at least one atom")
        if self.axis not in _AXES:
            raise ValueError("axis must be 'x', 'y', or 'z'")

    def __len__(self) -> int:
        return int(self.indices.size)

    @property
    def normal_index(self) -> int:
        """Return the Cartesian index normal to the selected layer."""

        return _AXES[self.axis]

    @property
    def in_plane_axes(self) -> tuple[int, int]:
        """Return the two Cartesian indices lying in the selected plane."""

        return tuple(index for index in range(3) if index != self.normal_index)

    @property
    def in_plane_labels(self) -> tuple[str, str]:
        """Return the Cartesian labels of the two in-plane axes."""

        labels = ("x", "y", "z")
        first, second = self.in_plane_axes
        return labels[first], labels[second]

    @property
    def projection_name(self) -> str:
        """Return the conventional name of the in-plane projection."""

        return "".join(self.in_plane_labels)


def _species_label(species: str | Sequence[str] | None) -> str:
    if species is None:
        return "all species"
    names = [species] if isinstance(species, str) else list(species)
    return ", ".join(names)


def _automatic_edge_layer(
    coordinates: NDArray[np.float64], side: str
) -> tuple[NDArray[np.int64], float]:
    """Cluster one-dimensional coordinates and return an edge layer.

    The split tolerance is inferred from the largest scale separation among
    adjacent coordinate gaps. Clean, repeated coordinate planes remain exact
    layers. If the inferred edge contains only one atom, the caller must supply
    an explicit tolerance instead of silently treating an outlier as a plane.
    """

    order = np.argsort(coordinates, kind="stable")
    ordered = coordinates[order]
    gaps = np.diff(ordered)
    scale = max(float(np.max(np.abs(ordered))), float(np.ptp(ordered)), 1.0)
    numerical_tolerance = 64.0 * np.finfo(np.float64).eps * scale
    meaningful = gaps[gaps > numerical_tolerance]

    if meaningful.size == 0:
        return order, numerical_tolerance
    if meaningful.size == 1:
        split_tolerance = float(meaningful[0] / 2.0)
    else:
        ranked = np.sort(meaningful)
        ratios = ranked[1:] / ranked[:-1]
        split_index = int(np.argmax(ratios))
        if ratios[split_index] >= 3.0:
            split_tolerance = float(
                np.sqrt(ranked[split_index] * ranked[split_index + 1])
            )
        else:
            split_tolerance = numerical_tolerance

    boundaries = np.flatnonzero(gaps > split_tolerance)
    if side == "max":
        start = int(boundaries[-1] + 1) if boundaries.size else 0
        chosen = order[start:]
    else:
        stop = int(boundaries[0] + 1) if boundaries.size else len(order)
        chosen = order[:stop]

    if chosen.size == 1 and coordinates.size > 1:
        raise ValueError(
            "automatic edge-layer detection found only one atom; "
            "provide an explicit coordinate tolerance"
        )
    return chosen, split_tolerance


def select_layer(
    frame: Frame,
    species: str | Sequence[str] | None = None,
    *,
    axis: str = "z",
    layer: str = "top",
    coordinate: float | None = None,
    tolerance: float | None = None,
) -> LayerSelection:
    """Select an atomic plane by edge layer or coordinate-centered slab.

    ``layer='top'`` and ``layer='bottom'`` mean the maximum and minimum edge
    along ``axis``. Without a tolerance, an edge layer is inferred from gaps in
    the selected species' coordinates. With ``coordinate``, atoms satisfying
    ``abs(position[axis] - coordinate) <= tolerance`` are selected explicitly.
    Coordinates and tolerances retain the trajectory's source position unit.
    """

    normalized_axis = axis.lower()
    if normalized_axis not in _AXES:
        raise ValueError("axis must be 'x', 'y', or 'z'")
    normalized_layer = layer.lower()
    if normalized_layer not in _LAYERS:
        raise ValueError("layer must be 'top', 'bottom', 'max', or 'min'")
    if coordinate is not None and not np.isfinite(coordinate):
        raise ValueError("coordinate must be finite")
    if tolerance is not None and (not np.isfinite(tolerance) or tolerance < 0):
        raise ValueError("tolerance must be a finite non-negative number")
    if coordinate is not None and tolerance is None:
        raise ValueError("coordinate selection requires an explicit tolerance")

    selected_species = (
        None
        if species is None
        else (species if isinstance(species, str) else list(species))
    )
    species_indices = np.flatnonzero(frame.species_mask(selected_species))
    if species_indices.size == 0:
        raise ValueError(f"no atoms match species selection {species!r}")

    axis_index = _AXES[normalized_axis]
    coordinates = np.asarray(
        frame.positions[species_indices, axis_index], dtype=np.float64
    )
    if not np.all(np.isfinite(coordinates)):
        raise ValueError("selected atom coordinates must be finite")

    side = _LAYERS[normalized_layer]
    if coordinate is not None:
        reference = float(coordinate)
        local_mask = np.abs(coordinates - reference) <= float(tolerance)
        local_indices = np.flatnonzero(local_mask)
        mode = "coordinate"
        used_tolerance = float(tolerance)
    elif tolerance is not None:
        reference = float(np.max(coordinates) if side == "max" else np.min(coordinates))
        local_indices = np.flatnonzero(
            np.abs(coordinates - reference) <= float(tolerance)
        )
        mode = f"{side}-edge"
        used_tolerance = float(tolerance)
    else:
        reference = float(np.max(coordinates) if side == "max" else np.min(coordinates))
        local_indices, used_tolerance = _automatic_edge_layer(coordinates, side)
        mode = f"auto-{side}-edge"

    if local_indices.size == 0:
        coordinate_range = (float(np.min(coordinates)), float(np.max(coordinates)))
        raise ValueError(
            f"no atoms lie within the requested {normalized_axis} selection; "
            f"available range is {coordinate_range[0]:.8g}..{coordinate_range[1]:.8g}"
        )

    indices = species_indices[local_indices]
    chosen_coordinates = coordinates[local_indices]
    return LayerSelection(
        indices=indices,
        axis=normalized_axis,
        mode=mode,
        reference_coordinate=reference,
        coordinate_min=float(np.min(chosen_coordinates)),
        coordinate_max=float(np.max(chosen_coordinates)),
        tolerance=used_tolerance,
        selection_label=_species_label(species),
    )
