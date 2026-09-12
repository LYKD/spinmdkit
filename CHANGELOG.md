# Changelog

All notable changes to SpinMDKit are documented here.

## 1.0.0 - 2026-09-12

### Changed

- Established `1.0.0` as the current stable baseline.
- Reframed SpinMDKit as a format-extensible spin-MD post-processing framework;
  Extended XYZ for NEP-spin/GPUMD is the first built-in adapter.
- Added a format-neutral reader contract, registry, automatic suffix selection,
  explicit CLI format selection, and format discovery.
- Centralized the package, CLI, and native-build version in `_version.py`.
- Documented maintainer-controlled semantic versioning with no automatic bumps.

## 0.1.0a1 - 2026-09-12

### Added

- Layered `data`, `io`, `kernels`, `analysis`, `visualization`, and `cli` modules.
- Streaming Extended XYZ reader with arbitrary property-schema preservation.
- Explicit local-moment, magnetization, Néel-vector, magnetic-force, and derived
  torque observables.
- CLI commands for inspection, CSV time-series export, and optional 3D plotting.
- NumPy backend with an optional C++17/pybind11 acceleration module.
- Cross-platform CI, wheel release automation, tests, examples, and architecture
  documentation.
