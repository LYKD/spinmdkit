"""SpinMDKit public API."""

from importlib.metadata import PackageNotFoundError, version

from .analysis import (
    magnetization,
    moment_norms,
    neel_vector,
    summarize_frame,
    torques,
)
from .data import Frame
from .io import ExtXYZError, Trajectory, iter_extxyz, read_frame
from .kernels import backend

try:
    __version__ = version("spinmdkit")
except PackageNotFoundError:
    __version__ = "0.1.0a1"

__all__ = [
    "ExtXYZError",
    "Frame",
    "Trajectory",
    "__version__",
    "backend",
    "iter_extxyz",
    "magnetization",
    "moment_norms",
    "neel_vector",
    "read_frame",
    "summarize_frame",
    "torques",
]
