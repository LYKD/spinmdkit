"""Magnetic observables with explicit physical semantics."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

from spinmdkit.kernels import row_cross, row_norms, row_sum


def moment_norms(spins: ArrayLike) -> NDArray[np.float64]:
    """Return the magnitude of each local magnetic moment."""

    return row_norms(spins)


def magnetization(spins: ArrayLike) -> NDArray[np.float64]:
    """Return the net magnetic-moment vector (a row-wise sum)."""

    return row_sum(spins)


def torques(spins: ArrayLike, magnetic_forces: ArrayLike) -> NDArray[np.float64]:
    """Return the derived row-wise ``spin x mforce`` vectors."""

    return row_cross(spins, magnetic_forces)


def neel_vector(spins: ArrayLike, sublattice_signs: ArrayLike) -> NDArray[np.float64]:
    """Return the signed mean moment for an explicitly supplied AFM partition."""

    spin_array = np.asarray(spins, dtype=np.float64)
    signs = np.asarray(sublattice_signs, dtype=np.float64)
    if spin_array.ndim != 2 or spin_array.shape[1] != 3:
        raise ValueError("spins must have shape (number_of_atoms, 3)")
    if signs.shape != (spin_array.shape[0],):
        raise ValueError("sublattice_signs must have one entry per selected atom")
    if spin_array.shape[0] == 0:
        raise ValueError("at least one spin is required")
    if not np.all(np.isin(signs, (-1.0, 1.0))):
        raise ValueError("sublattice_signs must contain only -1 and +1")
    return np.mean(spin_array * signs[:, None], axis=0)
