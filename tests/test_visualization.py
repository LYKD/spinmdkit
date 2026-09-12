import pytest

from spinmdkit import read_frame
from spinmdkit.analysis import analyze_moment_series
from spinmdkit.io import Trajectory
from spinmdkit.visualization import render_moment_series, render_spin_frame


def test_frame_renderer_is_an_independent_optional_layer(example_path, tmp_path):
    pytest.importorskip("matplotlib")
    output = tmp_path / "frame.png"
    render_spin_frame(
        read_frame(example_path),
        output,
        species="U",
        normalize=True,
        dpi=72,
    )
    assert output.is_file()
    assert output.stat().st_size > 1000


def test_moment_series_renderer_is_an_independent_optional_layer(
    example_path, tmp_path
):
    pytest.importorskip("matplotlib")
    series = analyze_moment_series(Trajectory(example_path), species="U")
    output = tmp_path / "moment-series.png"
    render_moment_series(series, output, dpi=72)
    assert output.is_file()
    assert output.stat().st_size > 1000
