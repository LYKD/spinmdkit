# Architecture

SpinMDKit is format-neutral at its core. It separates format adapters, validated
data, physical semantics, computation, and presentation. Extended XYZ for
current NEP-spin/GPUMD output is only the first built-in adapter. This avoids a
common failure mode in scientific post-processing: one plotting script quietly
becoming both the parser and the de facto data model.

```text
Any supported spin-MD trajectory
             |
             v
 reader registry -> isolated format adapter
             |
             v
  Frame(species, positions, cell,
        metadata, named properties)
             |
             v
  explicit observable functions
       |                 |
       v                 v
 NumPy fallback     C++17 kernels
       |                 |
       +--------+--------+
                v
          API / CLI outputs
          CSV / JSON / PNG
```

## Layers

### 1. I/O

`spinmdkit.io.TrajectoryReader` is the common adapter contract. The registry
selects a reader from an explicit format name or the longest matching suffix.
Each reader yields the same `Frame` object one frame at a time, so memory cost
can remain proportional to a frame rather than the full trajectory.

The first adapter, `ExtXYZReader`, uses the Extended XYZ `Properties` schema to
define column names, scalar types, and component counts. Unknown properties
remain accessible instead of being discarded. Future adapters live beside it
under `spinmdkit.io.readers` and do not require changes in downstream modules.

### 2. Data model

`Frame` owns required structural data and named atom properties. It validates
array lengths and vector shapes at the boundary. It does not infer units,
magnetic species, sublattices, or reference-versus-prediction provenance.

### 3. Observable layer

Small functions calculate local-moment norms, net magnetization, explicit-sign
Néel vectors, and `spin x mforce`. They operate on arrays and are independent of
the parser, which makes them reusable and directly testable.

### 4. Compute backend

`spinmdkit.core` presents one stable interface. Installed wheels contain a
pybind11 C++17 module for row-wise norms, sums, and cross products. A NumPy
fallback preserves the same semantics for source-tree use and constrained
systems.

### 5. Interfaces

The format-neutral `MomentSeries` analysis result is shared by CSV export and
plotting. `spinmdkit.export` owns dependency-light serializers, while
`spinmdkit.visualization` owns optional Matplotlib rendering. The CLI only
composes these operations. CSV uses flat, stable field names; JSON and
human-readable inspection output share the same summary values.

## Source layout and dependency direction

| Package | Responsibility | Allowed lower-level dependencies |
| --- | --- | --- |
| `data` | validated in-memory frame and property model | NumPy |
| `io` | reader contract, registry, adapters, and trajectory access | `data` |
| `kernels` | native/NumPy numerical implementation boundary | NumPy, optional `_core` |
| `analysis` | physical observable definitions and summaries | `data`, `kernels` |
| `export` | CSV and future dependency-light serializers | `analysis` |
| `visualization` | optional static rendering | `data`, `analysis`, Matplotlib on demand |
| `cli` | command arguments and composition | public modules above |

There are no imports from a lower layer back into a higher layer. A format
adapter can therefore be debugged without plotting, an observable can be tested
with a manually constructed `Frame`, and a renderer can be replaced without
changing trajectory interpretation.

## Extension points

Future readers implement `TrajectoryReader`, declare a canonical name and file
extensions, and yield the same `Frame`. They register through `register_reader`;
analysis and plotting remain untouched. New observables should accept arrays or
`Frame` plus an explicit selection. Domain inference—such as detecting AFM
sublattices—must return evidence and confidence rather than silently altering
the meaning of an observable.
