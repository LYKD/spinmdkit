"""Format-neutral trajectory I/O plus built-in format adapters."""

from .base import TrajectoryReader, TrajectorySource
from .extxyz import ExtXYZError, PropertySpec, iter_extxyz
from .registry import (
    FormatInfo,
    UnknownFormatError,
    available_formats,
    get_reader,
    iter_frames,
    read_frame,
    register_reader,
    resolve_reader,
    unregister_reader,
)
from .trajectory import Trajectory

__all__ = [
    "ExtXYZError",
    "FormatInfo",
    "PropertySpec",
    "Trajectory",
    "TrajectoryReader",
    "TrajectorySource",
    "UnknownFormatError",
    "available_formats",
    "get_reader",
    "iter_extxyz",
    "iter_frames",
    "read_frame",
    "register_reader",
    "resolve_reader",
    "unregister_reader",
]
