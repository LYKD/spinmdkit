# Architecture

SpinMDKit separates file interpretation, physical semantics, computation, and
presentation. This avoids a common failure mode in scientific post-processing:
a plotting script quietly becoming the de facto data model.

```text
Extended XYZ / GPUMD trajectory
             |
             v
   schema-driven stream reader
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

`spinmdkit.io.iter_extxyz` reads one frame at a time. Its memory cost is
proportional to a frame rather than the full trajectory. The `Properties`
schema defines column names, scalar types, and component counts; unknown
properties remain accessible instead of being discarded.

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

The CLI composes the same public API used by Python callers. CSV uses flat,
stable field names. JSON and human-readable inspection output share the same
summary values. Matplotlib is an optional dependency isolated to plotting.

## Source layout and dependency direction

| Package | Responsibility | Allowed lower-level dependencies |
| --- | --- | --- |
| `data` | validated in-memory frame and property model | NumPy |
| `io` | Extended XYZ parsing and trajectory access | `data` |
| `kernels` | native/NumPy numerical implementation boundary | NumPy, optional `_core` |
| `analysis` | physical observable definitions and summaries | `data`, `kernels` |
| `visualization` | optional static rendering | `data`, Matplotlib on demand |
| `cli` | command arguments and composition | public modules above |

There are no imports from a lower layer back into a higher layer. A parser can
therefore be debugged without plotting, an observable can be tested with a
manually constructed `Frame`, and a renderer can be replaced without changing
trajectory interpretation.

## Extension points

Future readers should yield the same `Frame`. New observables should accept
arrays or `Frame` plus an explicit selection. Domain inference—such as detecting
AFM sublattices—must return evidence and confidence rather than silently
altering the meaning of an observable.
