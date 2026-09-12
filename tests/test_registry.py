from io import StringIO

import numpy as np
import pytest

from spinmdkit import Frame, Trajectory, available_formats, iter_frames, read_frame
from spinmdkit.io import (
    UnknownFormatError,
    register_reader,
    resolve_reader,
    unregister_reader,
)


class DummyReader:
    name = "dummy-test"
    extensions = (".spin-test",)

    def iter_frames(self, source):
        del source
        yield Frame(
            species=np.array(["X"]),
            positions=np.zeros((1, 3)),
            properties={"spin": np.array([[0.0, 0.0, 1.0]])},
            metadata={"adapter": self.name},
        )


def test_builtin_format_is_discoverable_and_auto_selected(example_path):
    names = {item.name for item in available_formats()}
    assert "extxyz" in names
    assert resolve_reader(example_path).name == "extxyz"
    assert Trajectory(example_path).resolved_format == "extxyz"


def test_stream_requires_explicit_format():
    stream = StringIO("1\nProperties=species:S:1:pos:R:3:spin:R:3\nX 0 0 0 0 0 1\n")
    with pytest.raises(UnknownFormatError, match="explicit format"):
        next(iter_frames(stream))
    stream.seek(0)
    assert len(next(iter_frames(stream, "extxyz"))) == 1


def test_new_format_adapter_does_not_change_analysis_or_data_layers():
    register_reader(DummyReader(), aliases=("dummy-alias",))
    try:
        trajectory = Trajectory("anything.spin-test")
        frame = trajectory.frame()
        assert trajectory.resolved_format == "dummy-test"
        assert frame.metadata["adapter"] == "dummy-test"
        assert resolve_reader("ignored", "dummy-alias").name == "dummy-test"
    finally:
        unregister_reader("dummy-test")


def test_unknown_suffix_has_actionable_error():
    with pytest.raises(UnknownFormatError, match="--format"):
        list(iter_frames("trajectory.unknown"))


def test_negative_frame_index_reads_from_the_end(example_path):
    assert read_frame(example_path, -1).metadata["Time"] == 1.0
    with pytest.raises(IndexError, match="frame -3"):
        read_frame(example_path, -3)
