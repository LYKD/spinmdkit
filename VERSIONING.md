# Versioning policy

SpinMDKit uses maintainer-controlled semantic versioning.

The version changes only after an explicit instruction from the maintainer. A
commit, debugging session, pull request, CI run, or feature implementation does
not change the version by itself. Contributors should not edit the version in a
pull request unless the maintainer explicitly requests it.

Given a current version `MAJOR.MINOR.PATCH`:

- a requested debugging or bug-fix release increments `PATCH`, for example
  `1.0.0` to `1.0.1`;
- a requested feature release increments `MINOR` and resets `PATCH`, for example
  `1.0.1` to `1.1.0`;
- a requested major-change release increments `MAJOR` and resets the remaining
  fields, for example `1.1.0` to `2.0.0`.

The current version is `1.0.0`. The single source of truth is
`src/spinmdkit/_version.py`; packaging metadata, the CLI, and native builds read
from that file.
