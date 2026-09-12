"""Stable numerical API with native and NumPy implementations."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

try:
    from spinmdkit import _core as _native
except ImportError:
    _native = None


def _vectors(values: ArrayLike, name: str) -> NDArray[np.float64]:
    array = np.ascontiguousarray(values, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError(f"{name} must have shape (number_of_atoms, 3)")
    return array


def backend() -> str:
    """Return ``native`` when the C++ kernel is available, otherwise ``numpy``."""

    return "native" if _native is not None else "numpy"


def row_norms(values: ArrayLike) -> NDArray[np.float64]:
    array = _vectors(values, "values")
    if _native is not None:
        return _native.row_norms(array)
    return np.linalg.norm(array, axis=1)


def row_sum(values: ArrayLike) -> NDArray[np.float64]:
    array = _vectors(values, "values")
    if _native is not None:
        return _native.row_sum(array)
    return np.sum(array, axis=0)


def row_cross(left: ArrayLike, right: ArrayLike) -> NDArray[np.float64]:
    left_array = _vectors(left, "left")
    right_array = _vectors(right, "right")
    if left_array.shape != right_array.shape:
        raise ValueError("left and right must have the same shape")
    if _native is not None:
        return _native.row_cross(left_array, right_array)
    return np.cross(left_array, right_array)
