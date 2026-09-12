import csv
import json

from spinmdkit.cli import main


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


def test_bad_pattern_is_reported(example_path, capsys):
    code = main(
        ["inspect", str(example_path), "--species", "U", "--sublattice-pattern", "+-"]
    )
    assert code == 0
    assert "neel_norm" in capsys.readouterr().out
