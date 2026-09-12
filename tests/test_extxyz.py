from io import StringIO

import numpy as np
import pytest

from spinmdkit.io import ExtXYZError, Trajectory, iter_extxyz, read_frame

TEXT = """2
Time=12.5 pbc="T T F" Lattice="2 0 0 0 3 0 0 0 4" stress="1 0 0 0 2 0 0 0 3" Properties=species:S:1:pos:R:3:spin:R:3:mforce:R:3:spin_velocity:R:3:id:I:1
U 0 0 0 0 0 2 0.1 0 0 0 0.2 0 10
N 1 1 1 0 0 0 0 0 0 0 0 0 11
"""


def test_reader_preserves_named_spin_properties_and_metadata():
    frame = next(iter_extxyz(StringIO(TEXT)))
    assert frame.species.tolist() == ["U", "N"]
    assert frame.positions.shape == (2, 3)
    assert set(frame.properties) == {"spin", "mforce", "spin_velocity", "id"}
    np.testing.assert_allclose(frame.cell, np.diag([2.0, 3.0, 4.0]))
    np.testing.assert_allclose(frame.metadata["stress"], np.diag([1.0, 2.0, 3.0]))
    assert frame.metadata["pbc"] == (True, True, False)
    assert frame.metadata["Time"] == 12.5
    assert frame.properties["id"].dtype == np.int64


def test_read_frame_uses_zero_based_index(tmp_path):
    trajectory = tmp_path / "two.xyz"
    trajectory.write_text(
        TEXT + TEXT.replace("Time=12.5", "Time=13.5"), encoding="utf-8"
    )
    assert read_frame(trajectory, 1).metadata["Time"] == 13.5
    with pytest.raises(IndexError):
        read_frame(trajectory, 2)


def test_trajectory_facade_keeps_storage_access_separate(tmp_path):
    path = tmp_path / "trajectory.xyz"
    path.write_text(TEXT, encoding="utf-8")
    trajectory = Trajectory(path)
    assert trajectory.frame().metadata["Time"] == 12.5
    assert len(list(trajectory)) == 1


def test_incomplete_frame_reports_context():
    broken = "2\nProperties=species:S:1:pos:R:3\nU 0 0 0\n"
    with pytest.raises(ExtXYZError, match="ended after 1 of 2 atoms"):
        list(iter_extxyz(StringIO(broken)))


def test_column_mismatch_is_rejected():
    broken = "1\nProperties=species:S:1:pos:R:3:spin:R:3\nU 0 0 0 1 2\n"
    with pytest.raises(ExtXYZError, match="expected 7 columns, got 6"):
        list(iter_extxyz(StringIO(broken)))


def test_duplicate_property_names_are_rejected():
    broken = (
        "1\nProperties=species:S:1:pos:R:3:spin:R:3:spin:R:3\nU 0 0 0 1 0 0 1 0 0\n"
    )
    with pytest.raises(ExtXYZError, match="duplicate property"):
        list(iter_extxyz(StringIO(broken)))
