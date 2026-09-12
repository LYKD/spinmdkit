import pytest

from spinmdkit import read_frame, select_layer
from spinmdkit.analysis import analyze_moment_series
from spinmdkit.io import Trajectory
from spinmdkit.visualization import (
    render_moment_series,
    render_spin_frame,
    render_spin_layer,
)


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


def test_layer_renderer_preserves_svg_text_and_magnitude_range(example_path, tmp_path):
    pytest.importorskip("matplotlib")
    frame = read_frame(example_path, -1)
    selection = select_layer(frame, "U", axis="z", layer="top")
    output = tmp_path / "layer.svg"

    outputs = render_spin_layer(
        frame,
        selection,
        output,
        moment_unit="μB",
        position_unit="Å",
    )

    assert outputs == (
        output,
        output.with_suffix(".pdf"),
        output.with_suffix(".png"),
    )
    assert all(path.is_file() for path in outputs)
    svg = output.read_text(encoding="utf-8")
    assert "In-plane moment magnitude (μB)" in svg
    assert "xy projection" in svg
    assert "Arrow scale" in svg
    assert "<text" in svg


def test_x_layer_projection_uses_the_yz_plane(example_path, tmp_path):
    pytest.importorskip("matplotlib")
    frame = read_frame(example_path, -1)
    selection = select_layer(frame, "U", axis="x", layer="top")
    output = tmp_path / "x-layer.svg"

    render_spin_layer(frame, selection, output, moment_unit="μB", position_unit="Å")

    svg = output.read_text(encoding="utf-8")
    assert "yz projection" in svg
    assert "my, mz only" in svg
    assert "y (Å)" in svg
    assert "z (Å)" in svg
