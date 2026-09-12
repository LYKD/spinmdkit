from pathlib import Path

import pytest


@pytest.fixture
def example_path() -> Path:
    return (
        Path(__file__).parents[1]
        / "examples"
        / "afm_frame"
        / "trajectory.xyz"
    )
