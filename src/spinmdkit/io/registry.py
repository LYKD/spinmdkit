"""Dependency-free registry for present and future trajectory formats."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from threading import RLock

from spinmdkit.data import Frame

from .base import TrajectoryReader, TrajectorySource


class UnknownFormatError(ValueError):
    """Raised when no registered reader can interpret a source."""


@dataclass(frozen=True, slots=True)
class FormatInfo:
    """Public, immutable description of one registered reader."""

    name: str
    extensions: tuple[str, ...]
    aliases: tuple[str, ...]


_READERS: dict[str, TrajectoryReader] = {}
_ALIASES: dict[str, str] = {}
_LOCK = RLock()


def _normalized_name(name: str) -> str:
    normalized = name.strip().lower()
    if not normalized or not normalized.replace("-", "").replace("_", "").isalnum():
        raise ValueError(f"invalid format name {name!r}")
    return normalized


def register_reader(
    reader: TrajectoryReader,
    *,
    aliases: tuple[str, ...] = (),
    replace: bool = False,
) -> None:
    """Register a format adapter without coupling it to analysis or plotting."""

    name = _normalized_name(reader.name)
    extensions = tuple(extension.lower() for extension in reader.extensions)
    if not extensions or any(not extension.startswith(".") for extension in extensions):
        raise ValueError(
            "reader extensions must be non-empty strings beginning with '.'"
        )
    normalized_aliases = tuple(_normalized_name(alias) for alias in aliases)
    if name in normalized_aliases:
        raise ValueError("a reader name cannot also be its alias")
    with _LOCK:
        collisions = [
            candidate
            for candidate in (name, *normalized_aliases)
            if candidate in _READERS or candidate in _ALIASES
        ]
        if collisions and not replace:
            raise ValueError(
                f"format name or alias already registered: {collisions[0]!r}"
            )
        if replace and name in _READERS:
            for alias, target in tuple(_ALIASES.items()):
                if target == name:
                    del _ALIASES[alias]
        _READERS[name] = reader
        for alias in normalized_aliases:
            _ALIASES[alias] = name


def unregister_reader(name: str) -> None:
    """Remove a reader, primarily for tests and optional application adapters."""

    normalized = _normalized_name(name)
    with _LOCK:
        canonical = _ALIASES.get(normalized, normalized)
        if canonical not in _READERS:
            raise UnknownFormatError(f"format {name!r} is not registered")
        del _READERS[canonical]
        for alias, target in tuple(_ALIASES.items()):
            if target == canonical:
                del _ALIASES[alias]


def available_formats() -> tuple[FormatInfo, ...]:
    """Return registered formats in stable name order."""

    with _LOCK:
        result = []
        for name, reader in sorted(_READERS.items()):
            aliases = tuple(
                sorted(alias for alias, target in _ALIASES.items() if target == name)
            )
            result.append(FormatInfo(name, tuple(reader.extensions), aliases))
        return tuple(result)


def get_reader(name: str) -> TrajectoryReader:
    """Resolve a canonical format name or alias."""

    normalized = _normalized_name(name)
    with _LOCK:
        canonical = _ALIASES.get(normalized, normalized)
        try:
            return _READERS[canonical]
        except KeyError as exc:
            choices = ", ".join(sorted(_READERS)) or "none"
            raise UnknownFormatError(
                f"unknown format {name!r}; registered formats: {choices}"
            ) from exc


def resolve_reader(
    source: TrajectorySource,
    format_name: str | None = None,
) -> TrajectoryReader:
    """Resolve an explicit format or infer one from the longest file suffix."""

    if format_name and format_name.lower() != "auto":
        return get_reader(format_name)
    source_name = getattr(source, "name", source)
    if not isinstance(source_name, (str, Path)):
        raise UnknownFormatError("stream inputs require an explicit format name")
    lowered = str(source_name).lower()
    with _LOCK:
        candidates = [
            (len(extension), reader)
            for reader in _READERS.values()
            for extension in reader.extensions
            if lowered.endswith(extension.lower())
        ]
    if not candidates:
        suffix = "".join(Path(lowered).suffixes) or "(none)"
        raise UnknownFormatError(
            f"cannot infer a reader for suffix {suffix!r}; use --format explicitly"
        )
    candidates.sort(key=lambda item: item[0], reverse=True)
    longest = candidates[0][0]
    readers = {
        reader.name: reader for length, reader in candidates if length == longest
    }
    if len(readers) > 1:
        choices = ", ".join(sorted(readers))
        raise UnknownFormatError(f"ambiguous format; choose one explicitly: {choices}")
    return next(iter(readers.values()))


def iter_frames(
    source: TrajectorySource,
    format_name: str | None = None,
) -> Iterator[Frame]:
    """Yield frames through the selected format adapter."""

    return resolve_reader(source, format_name).iter_frames(source)


def read_frame(
    source: TrajectorySource,
    index: int = 0,
    format_name: str | None = None,
) -> Frame:
    """Read one zero-based frame through the selected adapter."""

    if index < 0:
        raise ValueError("index must be non-negative")
    for frame_index, frame in enumerate(iter_frames(source, format_name)):
        if frame_index == index:
            return frame
    raise IndexError(f"trajectory has no frame {index}")


from .readers import ExtXYZReader

register_reader(ExtXYZReader(), aliases=("xyz",))
