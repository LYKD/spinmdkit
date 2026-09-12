"""Physical post-processing independent of I/O and plotting."""

from .moment_series import MomentSeries, analyze_moment_series
from .observables import magnetization, moment_norms, neel_vector, torques
from .summary import summarize_frame

__all__ = [
    "MomentSeries",
    "analyze_moment_series",
    "magnetization",
    "moment_norms",
    "neel_vector",
    "summarize_frame",
    "torques",
]
