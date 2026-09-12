"""Frame-level summaries composed from small observable functions."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import ArrayLike

from spinmdkit.data import Frame
from spinmdkit.kernels import backend, row_norms

from .observables import magnetization, moment_norms, neel_vector, torques


def _vector(values: np.ndarray) -> list[float]:
    return [float(value) for value in values]


def summarize_frame(
    frame: Frame,
    species: str | Sequence[str] | None = None,
    sublattice_signs: ArrayLike | None = None,
) -> dict[str, object]:
    """Produce a JSON-ready summary for one frame without unit conversion."""

    selected = (
        None
        if species is None
        else (species if isinstance(species, str) else list(species))
    )
    mask = frame.species_mask(selected)
    if not np.any(mask):
        raise ValueError(f"no atoms match species selection {species!r}")
    spins = frame.spins[mask]
    count = len(spins)
    norms = moment_norms(spins)
    total = magnetization(spins)
    result: dict[str, object] = {
        "atoms": int(count),
        "backend": backend(),
        "magnetization": _vector(total),
        "magnetization_norm": float(np.linalg.norm(total)),
        "magnetization_per_atom": _vector(total / count),
        "mean_moment_norm": float(np.mean(norms)),
        "min_moment_norm": float(np.min(norms)),
        "max_moment_norm": float(np.max(norms)),
    }
    if sublattice_signs is not None:
        neel = neel_vector(spins, sublattice_signs)
        result["neel_vector"] = _vector(neel)
        result["neel_norm"] = float(np.linalg.norm(neel))
    if "mforce" in frame.properties:
        magnetic_forces = frame.vector_property("mforce")[mask]
        force_norms = row_norms(magnetic_forces)
        torque_norms = row_norms(torques(spins, magnetic_forces))
        result.update(
            {
                "mean_mforce_norm": float(np.mean(force_norms)),
                "max_mforce_norm": float(np.max(force_norms)),
                "mean_torque_norm": float(np.mean(torque_norms)),
                "max_torque_norm": float(np.max(torque_norms)),
            }
        )
    return result
