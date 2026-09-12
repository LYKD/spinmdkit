"""Command-line interface for trajectory inspection and visualization."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from itertools import islice
from pathlib import Path

import numpy as np

from ._version import __version__
from .analysis import analyze_moment_series, summarize_frame
from .export import write_moment_series_csv
from .io import ExtXYZError, Trajectory, available_formats
from .visualization import render_moment_series, render_spin_frame


def _selection(values: list[str] | None):
    if not values:
        return None
    return values[0] if len(values) == 1 else values


def _signs(pattern: str | None, count: int) -> np.ndarray | None:
    if pattern is None:
        return None
    symbols = [character for character in pattern if character in "+-"]
    unexpected = [
        character for character in pattern if character not in "+- ,;:_|\t\r\n"
    ]
    if unexpected or not symbols:
        raise ValueError("sublattice pattern must contain only '+' and '-' separators")
    if count % len(symbols):
        raise ValueError(
            f"pattern length {len(symbols)} does not divide the {count} selected atoms"
        )
    unit = np.asarray([1.0 if symbol == "+" else -1.0 for symbol in symbols])
    return np.tile(unit, count // len(unit))


def _limited_frames(trajectory: Trajectory, maximum: int | None):
    frames = iter(trajectory)
    if maximum is not None:
        frames = islice(frames, maximum)
    yield from enumerate(frames)


def _inspect(args: argparse.Namespace) -> int:
    selection = _selection(args.species)
    trajectory = Trajectory(args.input, args.format)
    frame_count = 0
    atom_counts: list[int] = []
    selected_counts: list[int] = []
    moment_means: list[float] = []
    magnetization_norms: list[float] = []
    times: list[float] = []
    species_counts: Counter[str] = Counter()
    properties: list[str] = []
    maxima: dict[str, float] = {}
    compute_backend = "unknown"

    for _, frame in _limited_frames(trajectory, args.max_frames):
        mask = frame.species_mask(selection)
        signs = _signs(args.sublattice_pattern, int(np.sum(mask)))
        summary = summarize_frame(frame, selection, signs)
        if frame_count == 0:
            species_counts.update(frame.species.tolist())
            properties = sorted(frame.properties)
            compute_backend = str(summary["backend"])
        frame_count += 1
        atom_counts.append(len(frame))
        selected_counts.append(int(summary["atoms"]))
        moment_means.append(float(summary["mean_moment_norm"]))
        magnetization_norms.append(float(summary["magnetization_norm"]))
        time_value = frame.metadata.get("Time")
        if isinstance(time_value, (int, float)):
            times.append(float(time_value))
        for name in ("max_mforce_norm", "max_torque_norm", "neel_norm"):
            if name in summary:
                maxima[name] = max(maxima.get(name, -np.inf), float(summary[name]))

    if frame_count == 0:
        raise ValueError("trajectory contains no frames")
    result: dict[str, object] = {
        "input": str(args.input),
        "format": trajectory.resolved_format,
        "frames": frame_count,
        "atoms_per_frame": [min(atom_counts), max(atom_counts)],
        "selected_atoms_per_frame": [min(selected_counts), max(selected_counts)],
        "species_first_frame": dict(sorted(species_counts.items())),
        "properties_first_frame": properties,
        "backend": compute_backend,
        "mean_moment_norm_range": [min(moment_means), max(moment_means)],
        "magnetization_norm_range": [
            min(magnetization_norms),
            max(magnetization_norms),
        ],
    }
    if times:
        result["time_raw_range"] = [times[0], times[-1]]
    result.update(maxima)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Input: {result['input']}")
        print(f"Frames: {frame_count}")
        print(f"Atoms/frame: {min(atom_counts)}..{max(atom_counts)}")
        print(f"Selected atoms/frame: {min(selected_counts)}..{max(selected_counts)}")
        print(f"First-frame species: {dict(sorted(species_counts.items()))}")
        print(f"First-frame properties: {', '.join(properties) or '(none)'}")
        print(f"Compute backend: {result['backend']}")
        print(
            "Mean local moment range: "
            f"{min(moment_means):.8g}..{max(moment_means):.8g} (source units)"
        )
        print(
            "Net moment norm range: "
            f"{min(magnetization_norms):.8g}..{max(magnetization_norms):.8g} (source units)"
        )
        if times:
            print(f"Time range: {times[0]:.8g}..{times[-1]:.8g} (source units)")
        for name, value in sorted(maxima.items()):
            print(f"{name}: {value:.8g} (source units)")
    return 0


def _timeseries(args: argparse.Namespace) -> int:
    selection = _selection(args.species)
    trajectory = Trajectory(args.input, args.format)
    if args.input.resolve() == args.output.resolve():
        raise ValueError("input and output paths must be different")
    fieldnames = [
        "frame",
        "time_raw",
        "atoms",
        "magnetization_x",
        "magnetization_y",
        "magnetization_z",
        "magnetization_norm",
        "magnetization_per_atom_x",
        "magnetization_per_atom_y",
        "magnetization_per_atom_z",
        "mean_moment_norm",
        "min_moment_norm",
        "max_moment_norm",
        "neel_x",
        "neel_y",
        "neel_z",
        "neel_norm",
        "max_mforce_norm",
        "max_torque_norm",
    ]
    written = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for frame_index, frame in _limited_frames(trajectory, args.max_frames):
            mask = frame.species_mask(selection)
            signs = _signs(args.sublattice_pattern, int(np.sum(mask)))
            summary = summarize_frame(frame, selection, signs)
            magnetization = summary["magnetization"]
            per_atom = summary["magnetization_per_atom"]
            neel = summary.get("neel_vector", ["", "", ""])
            writer.writerow(
                {
                    "frame": frame_index,
                    "time_raw": frame.metadata.get("Time", ""),
                    "atoms": summary["atoms"],
                    "magnetization_x": magnetization[0],
                    "magnetization_y": magnetization[1],
                    "magnetization_z": magnetization[2],
                    "magnetization_norm": summary["magnetization_norm"],
                    "magnetization_per_atom_x": per_atom[0],
                    "magnetization_per_atom_y": per_atom[1],
                    "magnetization_per_atom_z": per_atom[2],
                    "mean_moment_norm": summary["mean_moment_norm"],
                    "min_moment_norm": summary["min_moment_norm"],
                    "max_moment_norm": summary["max_moment_norm"],
                    "neel_x": neel[0],
                    "neel_y": neel[1],
                    "neel_z": neel[2],
                    "neel_norm": summary.get("neel_norm", ""),
                    "max_mforce_norm": summary.get("max_mforce_norm", ""),
                    "max_torque_norm": summary.get("max_torque_norm", ""),
                }
            )
            written += 1
    if written == 0:
        raise ValueError("trajectory contains no frames")
    print(f"Wrote {written} frame(s) to {args.output}")
    return 0


def _plot_moments(args: argparse.Namespace) -> int:
    data_output = args.data_output or args.output.with_suffix(".csv")
    resolved_paths = {
        "input": args.input.resolve(),
        "figure": args.output.resolve(),
        "data": data_output.resolve(),
    }
    if len(set(resolved_paths.values())) != len(resolved_paths):
        raise ValueError("input, figure output, and data output must be different")
    selection = _selection(args.species)
    trajectory = Trajectory(args.input, args.format)
    series = analyze_moment_series(
        trajectory,
        selection,
        timestep=args.timestep,
        sample_every=args.sample_every,
        time_offset=args.time_offset,
        time_source=args.time_source,
        time_key=args.time_key,
        time_scale=args.time_scale,
        time_unit=args.time_unit,
        moment_unit=args.moment_unit,
        frame_stride=args.frame_stride,
        max_frames=args.max_frames,
    )
    write_moment_series_csv(series, data_output)
    render_moment_series(
        series,
        args.output,
        dpi=args.dpi,
        title=args.title,
    )
    print(
        f"Analyzed {len(series)} frame(s); time "
        f"{series.times[0]:.8g}..{series.times[-1]:.8g} {series.time_unit}"
    )
    print(f"Wrote data: {data_output}")
    print(f"Wrote figure: {args.output}")
    return 0


def _plot_frame(args: argparse.Namespace) -> int:
    trajectory = Trajectory(args.input, args.format)
    frame = trajectory.frame(args.frame)
    selection = _selection(args.species)
    render_spin_frame(
        frame,
        args.output,
        species=selection,
        max_atoms=args.max_atoms,
        arrow_length=args.arrow_length,
        point_size=args.point_size,
        dpi=args.dpi,
        normalize=args.normalize,
        title=f"SpinMDKit frame {args.frame}",
    )
    print(f"Wrote {args.output}")
    return 0


def _formats(args: argparse.Namespace) -> int:
    formats = available_formats()
    if args.json:
        payload = [
            {
                "name": item.name,
                "extensions": list(item.extensions),
                "aliases": list(item.aliases),
            }
            for item in formats
        ]
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for item in formats:
            aliases = f" (aliases: {', '.join(item.aliases)})" if item.aliases else ""
            print(f"{item.name}: {', '.join(item.extensions)}{aliases}")
    return 0


def _add_format_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--format",
        default="auto",
        help="input format name or 'auto' (default: auto)",
    )


def _add_time_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--time-source",
        choices=("computed", "metadata"),
        default="computed",
        help="derive time from sampling settings or frame metadata (default: computed)",
    )
    parser.add_argument(
        "--timestep",
        type=float,
        default=1.0,
        help="MD integration timestep in --time-unit (default: 1)",
    )
    parser.add_argument(
        "--sample-every",
        type=int,
        default=1,
        help="MD steps between stored trajectory frames (default: 1)",
    )
    parser.add_argument(
        "--time-offset",
        type=float,
        default=0.0,
        help="constant added to every time value (default: 0)",
    )
    parser.add_argument(
        "--time-key",
        default="Time",
        help="numeric frame metadata key used by --time-source metadata",
    )
    parser.add_argument(
        "--time-scale",
        type=float,
        default=1.0,
        help="metadata time multiplier applied before the offset (default: 1)",
    )
    parser.add_argument(
        "--time-unit",
        default="step",
        help="time-axis label recorded in CSV and figure (default: step)",
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spinmdkit",
        description="Stream, analyze, and visualize spin molecular-dynamics trajectories.",
    )
    parser.add_argument(
        "--version", action="version", version=f"spinmdkit {__version__}"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    formats_parser = commands.add_parser(
        "formats", help="list registered input formats"
    )
    formats_parser.add_argument("--json", action="store_true")
    formats_parser.set_defaults(handler=_formats)

    inspect_parser = commands.add_parser("inspect", help="summarize a trajectory")
    inspect_parser.add_argument("input", type=Path)
    _add_format_argument(inspect_parser)
    inspect_parser.add_argument(
        "--species", nargs="+", help="one or more element symbols"
    )
    inspect_parser.add_argument(
        "--sublattice-pattern", help="explicit repeating '+'/'-' AFM pattern"
    )
    inspect_parser.add_argument("--max-frames", type=int)
    inspect_parser.add_argument("--json", action="store_true")
    inspect_parser.set_defaults(handler=_inspect)

    series_parser = commands.add_parser(
        "timeseries", help="export magnetic observables to CSV"
    )
    series_parser.add_argument("input", type=Path)
    _add_format_argument(series_parser)
    series_parser.add_argument("--output", "-o", type=Path, required=True)
    series_parser.add_argument(
        "--species", nargs="+", help="one or more element symbols"
    )
    series_parser.add_argument(
        "--sublattice-pattern", help="explicit repeating '+'/'-' AFM pattern"
    )
    series_parser.add_argument("--max-frames", type=int)
    series_parser.set_defaults(handler=_timeseries)

    moment_plot_parser = commands.add_parser(
        "plot-moments",
        help="export and plot magnetic-moment evolution",
    )
    moment_plot_parser.add_argument("input", type=Path)
    _add_format_argument(moment_plot_parser)
    moment_plot_parser.add_argument(
        "--output", "-o", type=Path, required=True, help="figure output path"
    )
    moment_plot_parser.add_argument(
        "--data-output",
        type=Path,
        help="CSV path (default: figure path with a .csv suffix)",
    )
    moment_plot_parser.add_argument(
        "--species", nargs="+", help="one or more element symbols"
    )
    _add_time_arguments(moment_plot_parser)
    moment_plot_parser.add_argument(
        "--moment-unit",
        default="source unit",
        help="moment-axis label recorded in CSV and figure",
    )
    moment_plot_parser.add_argument(
        "--frame-stride",
        type=int,
        default=1,
        help="analyze every Nth stored frame (default: 1)",
    )
    moment_plot_parser.add_argument("--max-frames", type=int)
    moment_plot_parser.add_argument("--dpi", type=int, default=180)
    moment_plot_parser.add_argument("--title")
    moment_plot_parser.set_defaults(handler=_plot_moments)

    plot_parser = commands.add_parser(
        "plot-frame", help="render one 3D spin-vector frame"
    )
    plot_parser.add_argument("input", type=Path)
    _add_format_argument(plot_parser)
    plot_parser.add_argument("--output", "-o", type=Path, required=True)
    plot_parser.add_argument("--frame", type=int, default=0)
    plot_parser.add_argument("--species", nargs="+", help="one or more element symbols")
    plot_parser.add_argument("--max-atoms", type=int, default=4000)
    plot_parser.add_argument("--arrow-length", type=float, default=1.0)
    plot_parser.add_argument("--point-size", type=float, default=8.0)
    plot_parser.add_argument("--dpi", type=int, default=180)
    plot_parser.add_argument("--normalize", action="store_true")
    plot_parser.set_defaults(handler=_plot_frame)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if getattr(args, "max_frames", None) is not None and args.max_frames < 1:
        parser.error("--max-frames must be positive")
    if getattr(args, "max_atoms", None) is not None and args.max_atoms < 1:
        parser.error("--max-atoms must be positive")
    if getattr(args, "dpi", None) is not None and args.dpi < 1:
        parser.error("--dpi must be positive")
    if getattr(args, "sample_every", None) is not None and args.sample_every < 1:
        parser.error("--sample-every must be positive")
    if getattr(args, "frame_stride", None) is not None and args.frame_stride < 1:
        parser.error("--frame-stride must be positive")
    if getattr(args, "arrow_length", None) is not None and args.arrow_length <= 0:
        parser.error("--arrow-length must be positive")
    try:
        return int(args.handler(args))
    except (
        ExtXYZError,
        IndexError,
        KeyError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as exc:
        print(f"spinmdkit: error: {exc}", file=sys.stderr)
        return 2
