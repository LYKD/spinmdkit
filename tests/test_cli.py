import csv
import json
from pathlib import Path

import pytest

from spinmdkit import __version__
from spinmdkit.cli import main


def test_version_is_maintainer_assigned_1_0_0(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0
    assert capsys.readouterr().out.strip() == "spinmdkit 1.0.0"
    assert __version__ == "1.0.0"


def test_formats_command_lists_extxyz(capsys):
    assert main(["formats", "--json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result[0]["name"] == "extxyz"
    assert ".xyz" in result[0]["extensions"]


def test_inspect_json(example_path, capsys):
    code = main(
        [
            "inspect",
            str(example_path),
            "--species",
            "U",
            "--sublattice-pattern",
            "+--+",
            "--json",
        ]
    )
    result = json.loads(capsys.readouterr().out)
    assert code == 0
    assert result["frames"] == 2
    assert result["selected_atoms_per_frame"] == [4, 4]
    assert result["neel_norm"] == 2.0


def test_timeseries_csv(example_path, tmp_path):
    output = tmp_path / "series.csv"
    code = main(
        [
            "timeseries",
            str(example_path),
            "--output",
            str(output),
            "--species",
            "U",
            "--sublattice-pattern",
            "+--+",
        ]
    )
    assert code == 0
    with output.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 2
    assert rows[0]["time_raw"] == "0.0"
    assert rows[0]["neel_z"] == "2.0"
    assert rows[0]["min_moment_norm"] == "2.0"
    assert rows[0]["max_moment_norm"] == "2.0"


def test_plot_moments_writes_csv_and_horizontal_figure(tmp_path, capsys):
    pytest.importorskip("matplotlib")
    trajectory = (
        Path(__file__).parents[1]
        / "examples"
        / "moment_time_evolution"
        / "trajectory.xyz"
    )
    output = tmp_path / "moments.png"
    code = main(
        [
            "plot-moments",
            str(trajectory),
            "--species",
            "U",
            "--timestep",
            "0.001",
            "--sample-every",
            "100",
            "--time-offset",
            "0.2",
            "--time-unit",
            "ps",
            "--moment-unit",
            "μB",
            "--max-frames",
            "3",
            "--output",
            str(output),
        ]
    )
    assert code == 0
    assert output.is_file()
    assert output.stat().st_size > 1000
    data_output = output.with_suffix(".csv")
    with data_output.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert [float(row["time"]) for row in rows] == pytest.approx([0.2, 0.3, 0.4])
    assert rows[0]["time_unit"] == "ps"
    assert rows[0]["moment_unit"] == "μB"
    assert "Wrote figure" in capsys.readouterr().out


def test_plot_layer_selects_the_last_frame_top_u_plane(tmp_path, capsys):
    pytest.importorskip("matplotlib")
    trajectory = (
        Path(__file__).parents[1]
        / "examples"
        / "top_layer_moments"
        / "trajectory.xyz"
    )
    output = tmp_path / "top-layer.svg"

    code = main(
        [
            "plot-layer",
            str(trajectory),
            "--frame",
            "-1",
            "--species",
            "U",
            "--axis",
            "z",
            "--layer",
            "top",
            "--position-unit",
            "Å",
            "--moment-unit",
            "μB",
            "--output",
            str(output),
        ]
    )

    assert code == 0
    assert output.is_file()
    assert output.with_suffix(".pdf").is_file()
    assert output.with_suffix(".png").is_file()
    svg = output.read_text(encoding="utf-8")
    assert "In-plane moment magnitude (μB)" in svg
    assert "xy projection" in svg
    terminal_output = capsys.readouterr().out
    assert "Selected 9 atom(s) from frame -1" in terminal_output
    assert "z=3.98..4.03 Å" in terminal_output
    assert "In-plane (xy) moment magnitude range" in terminal_output
    assert terminal_output.count("Wrote ") == 3


def test_bad_pattern_is_reported(example_path, capsys):
    code = main(
        ["inspect", str(example_path), "--species", "U", "--sublattice-pattern", "+-"]
    )
    assert code == 0
    assert "neel_norm" in capsys.readouterr().out
