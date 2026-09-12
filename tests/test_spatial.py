import numpy as np
import pytest

from spinmdkit import Frame, select_layer


def _layered_frame() -> Frame:
    return Frame(
        species=np.array(["U", "U", "U", "U", "U", "U", "U", "N"]),
        positions=np.array(
            [
                [0.0, 0.0, -0.01],
                [1.0, 0.0, 0.00],
                [0.0, 1.0, 0.01],
                [0.0, 0.0, 3.99],
                [1.0, 0.0, 4.00],
                [0.0, 1.0, 4.01],
                [1.0, 1.0, 4.02],
                [0.5, 0.5, 5.00],
            ]
        ),
        properties={"spin": np.ones((8, 3))},
    )


def test_automatic_top_layer_selects_a_plane_not_the_maximum_atom():
    selection = select_layer(_layered_frame(), "U", axis="z", layer="top")

    np.testing.assert_array_equal(selection.indices, [3, 4, 5, 6])
    assert selection.mode == "auto-max-edge"
    assert selection.coordinate_min == pytest.approx(3.99)
    assert selection.coordinate_max == pytest.approx(4.02)
    assert selection.in_plane_axes == (0, 1)
    assert selection.in_plane_labels == ("x", "y")
    assert selection.projection_name == "xy"


def test_coordinate_selection_uses_an_explicit_symmetric_tolerance():
    selection = select_layer(
        _layered_frame(), "U", axis="z", coordinate=0.0, tolerance=0.011
    )

    np.testing.assert_array_equal(selection.indices, [0, 1, 2])
    assert selection.mode == "coordinate"


def test_automatic_edge_layer_rejects_a_single_outlier():
    frame = Frame(
        species=np.array(["U", "U", "U", "U"]),
        positions=np.array(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.1], [0.0, 1.0, 0.2], [1.0, 1.0, 4.0]]
        ),
        properties={"spin": np.ones((4, 3))},
    )

    with pytest.raises(ValueError, match="only one atom"):
        select_layer(frame, "U", axis="z", layer="top")


def test_coordinate_selection_requires_tolerance():
    with pytest.raises(ValueError, match="requires an explicit tolerance"):
        select_layer(_layered_frame(), "U", coordinate=4.0)
