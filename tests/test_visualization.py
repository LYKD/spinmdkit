import pytest

from spinmdkit import read_frame
from spinmdkit.visualization import render_spin_frame


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
