"""Physical post-processing independent of I/O and plotting."""

from .observables import magnetization, moment_norms, neel_vector, torques
from .summary import summarize_frame

__all__ = ["magnetization", "moment_norms", "neel_vector", "summarize_frame", "torques"]
