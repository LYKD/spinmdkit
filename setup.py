"""Optional native-extension definition for setuptools."""

from __future__ import annotations

import os

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

disabled = os.environ.get("SPINMDKIT_DISABLE_NATIVE", "").lower() in {
    "1",
    "true",
    "yes",
}
extensions = []
if not disabled:
    extensions.append(
        Pybind11Extension(
            "spinmdkit._core",
            ["cpp/core.cpp"],
            cxx_std=17,
            optional=True,
            define_macros=[("VERSION_INFO", '"0.1.0a1"')],
        )
    )

setup(ext_modules=extensions, cmdclass={"build_ext": build_ext})
