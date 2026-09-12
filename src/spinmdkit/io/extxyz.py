"""Streaming Extended XYZ reader with GPUMD spin-property support."""

from __future__ import annotations

import gzip
import shlex
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

import numpy as np

from spinmdkit.data import Frame


class ExtXYZError(ValueError):
    """Raised when an Extended XYZ stream is incomplete or inconsistent."""


@dataclass(frozen=True, slots=True)
class PropertySpec:
    name: str
    kind: str
    count: int


def _property_specs(raw: str, frame_index: int) -> list[PropertySpec]:
    fields = raw.split(":")
    if len(fields) % 3:
        raise ExtXYZError(f"frame {frame_index}: invalid Properties schema {raw!r}")
    specs: list[PropertySpec] = []
    for offset in range(0, len(fields), 3):
        name, kind, count_text = fields[offset : offset + 3]
        try:
            count = int(count_text)
        except ValueError as exc:
            raise ExtXYZError(
                f"frame {frame_index}: invalid component count {count_text!r}"
            ) from exc
        if not name or kind not in {"R", "I", "L", "S"} or count < 1:
            raise ExtXYZError(
                f"frame {frame_index}: invalid property triple {(name, kind, count_text)!r}"
            )
        specs.append(PropertySpec(name=name, kind=kind, count=count))
    return specs


def _parse_value(raw: str):
    lowered = raw.lower()
    if lowered in {"true", "t"}:
        return True
    if lowered in {"false", "f"}:
        return False
    try:
        return int(raw)
    except ValueError:
        try:
            return float(raw)
        except ValueError:
            return raw


def _comment_fields(comment: str, frame_index: int) -> dict[str, object]:
    try:
        tokens = shlex.split(comment, posix=True)
    except ValueError as exc:
        raise ExtXYZError(f"frame {frame_index}: malformed comment line") from exc
    fields: dict[str, object] = {"comment": comment}
    for token in tokens:
        if "=" not in token:
            fields.setdefault("labels", []).append(token)
            continue
        key, raw_value = token.split("=", 1)
        if key in {"Lattice", "stress", "virial"}:
            try:
                numbers = np.fromstring(raw_value, sep=" ", dtype=np.float64)
            except ValueError as exc:
                raise ExtXYZError(f"frame {frame_index}: invalid {key} values") from exc
            if numbers.size == 9:
                fields[key] = numbers.reshape(3, 3)
            else:
                fields[key] = numbers
        elif key == "pbc":
            values = raw_value.split()
            fields[key] = tuple(value.lower() in {"t", "true", "1"} for value in values)
        else:
            fields[key] = _parse_value(raw_value)
    return fields


def _convert_column(
    values: list[object], spec: PropertySpec, frame_index: int
) -> np.ndarray:
    try:
        if spec.kind == "R":
            return np.asarray(values, dtype=np.float64)
        if spec.kind == "I":
            return np.asarray(values, dtype=np.int64)
        if spec.kind == "L":
            converted = []
            for value in values:
                components = [value] if spec.count == 1 else value
                parsed = [
                    str(item).lower() in {"t", "true", "1"} for item in components
                ]
                converted.append(parsed[0] if spec.count == 1 else parsed)
            return np.asarray(converted, dtype=bool)
        return np.asarray(values, dtype=str)
    except (TypeError, ValueError) as exc:
        raise ExtXYZError(
            f"frame {frame_index}: values for property {spec.name!r} do not match type {spec.kind}"
        ) from exc


def _open_text(path: Path) -> TextIO:
    if path.suffix.lower() == ".gz":
        return gzip.open(path, mode="rt", encoding="utf-8", newline="")
    return path.open(mode="rt", encoding="utf-8", newline="")


def iter_extxyz(source: str | Path | TextIO) -> Iterator[Frame]:
    """Yield frames without loading the complete trajectory into memory."""

    owns_stream = not hasattr(source, "read")
    stream = _open_text(Path(source)) if owns_stream else source
    frame_index = 0
    line_number = 0
    try:
        while True:
            atom_count_line = stream.readline()
            line_number += 1
            while atom_count_line and not atom_count_line.strip():
                atom_count_line = stream.readline()
                line_number += 1
            if not atom_count_line:
                return
            try:
                atom_count = int(atom_count_line.strip())
            except ValueError as exc:
                raise ExtXYZError(
                    f"line {line_number}: expected atom count, got {atom_count_line.strip()!r}"
                ) from exc
            if atom_count < 1:
                raise ExtXYZError(f"line {line_number}: atom count must be positive")

            comment = stream.readline()
            line_number += 1
            if not comment:
                raise ExtXYZError(f"frame {frame_index}: missing comment line")
            metadata = _comment_fields(comment.rstrip("\r\n"), frame_index)
            raw_schema = metadata.get("Properties")
            if not isinstance(raw_schema, str):
                raise ExtXYZError(f"frame {frame_index}: missing Properties schema")
            specs = _property_specs(raw_schema, frame_index)
            names = [spec.name for spec in specs]
            if len(names) != len(set(names)):
                raise ExtXYZError(
                    f"frame {frame_index}: duplicate property names are not allowed"
                )
            expected_columns = sum(spec.count for spec in specs)
            raw_columns: dict[str, list[object]] = {spec.name: [] for spec in specs}

            for atom_index in range(atom_count):
                row = stream.readline()
                line_number += 1
                if not row:
                    raise ExtXYZError(
                        f"frame {frame_index}: ended after {atom_index} of {atom_count} atoms"
                    )
                tokens = row.split()
                if len(tokens) != expected_columns:
                    raise ExtXYZError(
                        f"line {line_number}: expected {expected_columns} columns, got {len(tokens)}"
                    )
                cursor = 0
                for spec in specs:
                    part = tokens[cursor : cursor + spec.count]
                    raw_columns[spec.name].append(part[0] if spec.count == 1 else part)
                    cursor += spec.count

            columns = {
                spec.name: _convert_column(raw_columns[spec.name], spec, frame_index)
                for spec in specs
            }
            if "species" not in columns or "pos" not in columns:
                raise ExtXYZError(
                    f"frame {frame_index}: schema must include species:S:1 and pos:R:3"
                )
            if columns["pos"].shape != (atom_count, 3):
                raise ExtXYZError(
                    f"frame {frame_index}: pos must contain three components"
                )
            cell = metadata.get("Lattice")
            if cell is not None and np.asarray(cell).shape != (3, 3):
                raise ExtXYZError(
                    f"frame {frame_index}: Lattice must contain nine values"
                )
            properties = {
                name: values
                for name, values in columns.items()
                if name not in {"species", "pos"}
            }
            yield Frame(
                species=columns["species"],
                positions=columns["pos"],
                properties=properties,
                cell=cell,
                metadata=metadata,
            )
            frame_index += 1
    finally:
        if owns_stream:
            stream.close()


def read_frame(source: str | Path | TextIO, index: int = 0) -> Frame:
    """Read one zero-based frame from a trajectory."""

    if index < 0:
        raise ValueError("index must be non-negative")
    for frame_index, frame in enumerate(iter_extxyz(source)):
        if frame_index == index:
            return frame
    raise IndexError(f"trajectory has no frame {index}")
