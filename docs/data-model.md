# Data model and conventions

## Frame

| Field | Shape | Meaning |
| --- | --- | --- |
| `species` | `(N,)` | element or site label from `species:S:1` |
| `positions` | `(N, 3)` | coordinates from `pos:R:3` |
| `cell` | `(3, 3)` or `None` | `Lattice` values in source order |
| `properties[name]` | `(N,)` or `(N, k)` | named Extended XYZ atom property |
| `metadata[key]` | scalar, string, or array | unmodified frame-level information |

The format-neutral model requires species labels and three-component positions.
Each adapter maps its source format into those fields and preserves additional
per-atom values in `properties` and frame-level information in `metadata`.

The built-in Extended XYZ adapter requires `species:S:1` and `pos:R:3`. It
retains all additional schema entries, including integer, real, logical, and
string values. Future formats need not use Extended XYZ names on disk; their
adapter is responsible for an explicit, documented mapping into `Frame`.

## Magnetic fields

`spin` must be a three-component per-atom property before a magnetic observable
is evaluated. `mforce` and `spin_velocity` are optional and remain distinct.
SpinMDKit never substitutes one field for another.

The first observable definitions are:

```text
local magnitude:  |s_i|
net moment:       M = sum_i s_i
Néel vector:      L = (1/N) sum_i eta_i s_i, eta_i in {-1, +1}
derived torque:   tau_i = s_i x mforce_i
```

Species selection happens before sublattice signs are applied. A repeating CLI
pattern must divide the number of selected atoms exactly.

## Units and provenance

Output units are inherited from input. Field names containing `raw` emphasize
that no unit conversion was performed. The library preserves stress and virial
arrays and does not assume a sign convention. Simulation predictions and
reference electronic-structure labels must be identified by the calling
workflow; the library does not promote one to the other.

## Moment time series

`MomentSeries` is a format-neutral analysis result. It contains original frame
indices, physical times, selected atom counts, net moment vectors and norms,
and the mean/minimum/maximum magnitude of selected local moments. It does not
contain parsing or plotting behavior.

For a computed time axis,

```text
t(frame) = time_offset + frame_index * timestep * sample_every
```

where `sample_every` describes the simulation output cadence. An independent
`frame_stride` can reduce post-processing density without changing the physical
times. Metadata time is opt-in and requires a named numeric key plus an explicit
scale, so an input label never silently overrides the requested time model.
