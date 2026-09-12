"""Core in-memory data model for one spin-MD frame."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray


@dataclass(slots=True)
class Frame:
    """A single atomistic frame with named per-atom properties.

    Positions and species have dedicated fields. Magnetic vectors such as
    ``spin``, ``mforce``, and ``spin_velocity`` remain explicitly named in
    ``properties`` so that predicted quantities are never silently relabeled.
    """

    species: NDArray[np.str_]
    positions: NDArray[np.float64]
    properties: dict[str, np.ndarray] = field(default_factory=dict)
    cell: NDArray[np.float64] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.species = np.asarray(self.species, dtype=str)
        self.positions = np.asarray(self.positions, dtype=np.float64)
        if self.species.ndim != 1:
            raise ValueError("species must be a one-dimensional array")
        if self.positions.shape != (len(self.species), 3):
            raise ValueError("positions must have shape (number_of_atoms, 3)")
        if self.cell is not None:
            self.cell = np.asarray(self.cell, dtype=np.float64)
            if self.cell.shape != (3, 3):
                raise ValueError("cell must have shape (3, 3)")
        normalized: dict[str, np.ndarray] = {}
        for name, values in self.properties.items():
            array = np.asarray(values)
            if array.ndim == 0 or array.shape[0] != len(self.species):
                raise ValueError(f"property {name!r} must contain one value per atom")
            normalized[name] = array
        self.properties = normalized

    def __len__(self) -> int:
        return len(self.species)

    @property
    def spins(self) -> NDArray[np.float64]:
        return self.vector_property("spin")

    @property
    def mforces(self) -> NDArray[np.float64]:
        return self.vector_property("mforce")

    def vector_property(self, name: str) -> NDArray[np.float64]:
        if name not in self.properties:
            raise KeyError(f"frame has no {name!r} property")
        values = np.asarray(self.properties[name], dtype=np.float64)
        if values.shape != (len(self), 3):
            raise ValueError(f"property {name!r} must have shape (number_of_atoms, 3)")
        return values

    def species_mask(
        self, selected: str | list[str] | tuple[str, ...] | None
    ) -> NDArray[np.bool_]:
        if selected is None:
            return np.ones(len(self), dtype=bool)
        names = [selected] if isinstance(selected, str) else list(selected)
        return np.isin(self.species, names)
