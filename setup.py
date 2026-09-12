"""Optional native-extension definition for setuptools."""

from __future__ import annotations

import os
import re
from pathlib import Path

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

disabled = os.environ.get("SPINMDKIT_DISABLE_NATIVE", "").lower() in {
    "1",
    "true",
    "yes",
}
version_text = (Path(__file__).parent / "src" / "spinmdkit" / "_version.py").read_text(
    encoding="utf-8"
)
version_match = re.search(r'^__version__ = "([^"]+)"$', version_text, re.MULTILINE)
if version_match is None:
    raise RuntimeError("unable to read SpinMDKit version")
package_version = version_match.group(1)
extensions = []
if not disabled:
    extensions.append(
        Pybind11Extension(
            "spinmdkit._core",
            ["cpp/core.cpp"],
            cxx_std=17,
            optional=True,
            define_macros=[("VERSION_INFO", f'"{package_version}"')],
        )
    )

setup(ext_modules=extensions, cmdclass={"build_ext": build_ext})
