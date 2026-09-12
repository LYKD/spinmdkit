import csv
from pathlib import Path

import numpy as np
import pytest

from spinmdkit.analysis import analyze_moment_series
from spinmdkit.export import write_moment_series_csv
from spinmdkit.io import Trajectory


def test_computed_time_axis_and_moment_statistics(example_path):
    series = analyze_moment_series(
        Trajectory(example_path),
        "U",
        timestep=0.002,
        sample_every=50,
        time_offset=0.3,
        time_unit="ps",
        moment_unit="μB",
    )
    np.testing.assert_array_equal(series.frame_indices, [0, 1])
    np.testing.assert_allclose(series.times, [0.3, 0.4])
    np.testing.assert_allclose(series.net_moments[0], [0.0, 0.0, 0.0])
    np.testing.assert_allclose(
        series.mean_moment_norms, [2.0, np.hypot(0.1, 1.99)]
    )
    np.testing.assert_allclose(series.min_moment_norms, series.max_moment_norms)


def test_metadata_time_is_explicitly_scaled_and_offset(example_path):
    series = analyze_moment_series(
        Trajectory(example_path),
        "U",
        time_source="metadata",
        time_key="Time",
        time_scale=0.5,
        time_offset=2.0,
        time_unit="ps",
    )
    np.testing.assert_allclose(series.times, [2.0, 2.5])


def test_frame_stride_preserves_original_physical_time():
    trajectory = (
        Path(__file__).parents[1]
        / "examples"
        / "moment_time_evolution"
        / "trajectory.xyz"
    )
    series = analyze_moment_series(
        Trajectory(trajectory),
        "U",
        timestep=0.001,
        sample_every=100,
        time_offset=0.2,
        frame_stride=3,
        max_frames=3,
    )
    np.testing.assert_array_equal(series.frame_indices, [0, 3, 6])
    np.testing.assert_allclose(series.times, [0.2, 0.5, 0.8])


def test_csv_export_contains_requested_moment_columns(example_path, tmp_path):
    series = analyze_moment_series(Trajectory(example_path), "U")
    target = write_moment_series_csv(series, tmp_path / "series.csv")
    with target.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 2
    assert float(rows[0]["net_moment_x"]) == 0.0
    assert float(rows[0]["mean_moment_norm"]) == 2.0
    assert float(rows[0]["min_moment_norm"]) == 2.0
    assert float(rows[0]["max_moment_norm"]) == 2.0


def test_invalid_time_configuration_is_reported(example_path):
    with pytest.raises(ValueError, match="sample_every"):
        analyze_moment_series(Trajectory(example_path), sample_every=0)
