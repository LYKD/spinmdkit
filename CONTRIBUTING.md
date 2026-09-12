# Contributing

SpinMDKit welcomes focused issues, small pull requests, and representative
GPUMD/NEP-spin test cases that can be redistributed.

## Development setup

```bash
git clone https://github.com/LYKD/spinmdkit.git
cd spinmdkit
python -m pip install -U pip
python -m pip install ".[dev]"
python -m pytest
```

Install `.[plot]` only when working on the independent visualization layer.

Do not change the version in a contribution unless the maintainer explicitly
requests it. See [VERSIONING.md](VERSIONING.md).

Contributions are accepted under the GNU General Public License version 3.
Submitting a contribution means you have the right to provide it under that
license. See [LICENSE](LICENSE).

Run the example CLI before submitting a change:

```bash
spinmdkit inspect examples/afm_frame/trajectory.xyz --species U \
  --sublattice-pattern "+--+" --json
```

## Design rules

- Preserve unknown input fields and source metadata.
- Keep format-specific parsing inside an isolated reader adapter.
- Make readers yield the common `Frame`; do not add format checks to analysis.
- Make physical conventions explicit in names and documentation.
- Do not infer AFM sublattices or change stress signs silently.
- Add tests for valid input, malformed input, and the physical value expected.
- Test spatial selectors separately from their renderers and report actual bounds.
- Keep plotting dependencies optional and computation independent of the CLI.
- Keep each example self-contained and include linked `README.md` and
  `README.zh-CN.md` files with equivalent commands and scientific definitions.

Do not commit proprietary trajectories, access tokens, private paths, or large
simulation outputs. Reduce a report to the smallest redistributable fixture.
