# Changelog

All notable changes to SpinMDKit are documented here.

## Unreleased (version remains 1.0.0)

### Added

- Added format-neutral magnetic-moment time-series analysis with explicit
  computed or metadata time axes, output cadence, offset, and frame stride.
- Added dependency-light CSV export and a horizontal two-panel plot for net
  `Mx/My/Mz/|M|` and mean/minimum/maximum local-moment magnitudes.
- Organized examples as self-contained directories with exact commands and
  generated outputs.
- Added reusable atomic-layer selection by edge or explicit coordinate slab,
  including end-relative frame indices such as `-1` for the last frame.
- Added side-by-side 3D and in-plane magnetic-moment arrows with automatic
  x-to-yz, y-to-xz, and z-to-xy projection rules and SVG/PDF/PNG output.

## 1.0.0 - 2026-09-12

### Changed

- Established `1.0.0` as the current stable baseline.
- Established a format-extensible spin-MD post-processing framework with
  built-in Extended XYZ support.
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
