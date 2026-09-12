"""SpinMDKit public API."""

from ._version import __version__
from .analysis import (
    magnetization,
    moment_norms,
    neel_vector,
    summarize_frame,
    torques,
)
from .data import Frame
from .io import (
    ExtXYZError,
    Trajectory,
    UnknownFormatError,
    available_formats,
    iter_extxyz,
    iter_frames,
    read_frame,
    register_reader,
)
from .kernels import backend

__all__ = [
    "ExtXYZError",
    "Frame",
    "Trajectory",
    "UnknownFormatError",
    "__version__",
    "available_formats",
    "backend",
    "iter_extxyz",
    "iter_frames",
    "magnetization",
    "moment_norms",
    "neel_vector",
    "read_frame",
    "register_reader",
    "summarize_frame",
    "torques",
]
