import numpy as np
import pytest

from spinmdkit import Frame
from spinmdkit.analysis import (
    magnetization,
    moment_norms,
    neel_vector,
    summarize_frame,
    torques,
)


def test_vector_observables_have_explicit_expected_values():
    spins = np.array([[0.0, 0.0, 2.0], [0.0, 0.0, -2.0]])
    magnetic_forces = np.array([[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    np.testing.assert_allclose(moment_norms(spins), [2.0, 2.0])
    np.testing.assert_allclose(magnetization(spins), [0.0, 0.0, 0.0])
    np.testing.assert_allclose(neel_vector(spins, [1, -1]), [0.0, 0.0, 2.0])
    np.testing.assert_allclose(torques(spins, magnetic_forces), [[0, 2, 0], [0, -2, 0]])


def test_summary_filters_species_before_afm_partition():
    frame = Frame(
        species=np.array(["U", "N", "U"]),
        positions=np.zeros((3, 3)),
        properties={
            "spin": np.array([[0, 0, 2], [0, 0, 0], [0, 0, -2]], dtype=float),
            "mforce": np.array([[1, 0, 0], [0, 0, 0], [1, 0, 0]], dtype=float),
        },
    )
    result = summarize_frame(frame, species="U", sublattice_signs=[1, -1])
    assert result["atoms"] == 2
    assert result["magnetization_norm"] == 0.0
    assert result["neel_vector"] == [0.0, 0.0, 2.0]
    assert result["max_torque_norm"] == 2.0


def test_neel_partition_must_be_explicit_and_valid():
    spins = np.zeros((2, 3))
    with pytest.raises(ValueError, match="one entry"):
        neel_vector(spins, [1])
    with pytest.raises(ValueError, match=r"only -1 and \+1"):
        neel_vector(spins, [0, 1])
