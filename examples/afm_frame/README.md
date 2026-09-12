<p align="center">
  <strong>English</strong> | <a href="README.zh-CN.md">简体中文</a>
</p>

# Explicit AFM frame example

This small two-frame trajectory demonstrates species selection and an explicit
repeating AFM sublattice pattern.

```bash
spinmdkit inspect examples/afm_frame/trajectory.xyz --species U \
  --sublattice-pattern "+--+" --json
```

The sublattice pattern is applied only to the four selected U atoms. SpinMDKit
does not infer AFM sublattices from atom order.
