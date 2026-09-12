# Adding a trajectory reader

SpinMDKit does not require a plugin manager to support another simulation
format. A reader is a small adapter that converts source records into the common
`Frame` model.

## Contract

A reader declares a canonical name, recognized extensions, and one streaming
method:

```python
from spinmdkit import Frame, register_reader


class MyReader:
    name = "my-format"
    extensions = (".myspin",)

    def iter_frames(self, source):
        for record in stream_source_records(source):
            yield Frame(
                species=record.species,
                positions=record.positions,
                cell=record.cell,
                properties={"spin": record.moments},
                metadata={"source_step": record.step},
            )


register_reader(MyReader(), aliases=("myspin",))
```

After registration, the standard API and CLI-facing trajectory layer can use
the format without changes to analysis or visualization:

```python
from spinmdkit import Trajectory

trajectory = Trajectory("run.myspin")
first_frame = trajectory.frame(0)
```

Built-in adapters are placed in `spinmdkit/io/readers/` and registered in the
I/O layer. Application-specific readers may be registered at application start.

## Reader requirements

- Stream frames instead of loading a complete production trajectory.
- Validate record sizes and raise errors with frame or line context.
- Map positions and species explicitly into `Frame`.
- Preserve additional atom fields in `properties` and source metadata in
  `metadata`.
- Document units, signs, coordinate conventions, and provenance; do not perform
  silent conversions.
- Keep optional parser dependencies inside the adapter that needs them.
- Add malformed-input, mapping, auto-detection, and round-trip tests when a
  writer is introduced.

The adapter boundary is intentionally based on ordinary Python objects. Users
do not need to install a separate plugin system.
