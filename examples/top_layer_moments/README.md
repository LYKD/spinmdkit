<p align="center">
  <strong>English</strong> | <a href="README.zh-CN.md">简体中文</a>
</p>

# Top-layer magnetic-moment arrows

This example reads the last trajectory frame, selects U atoms, identifies the
upper z layer as one atomic plane, and renders every selected magnetic moment.
The top layer contains nine U atoms with a small z corrugation, so the selection
does not rely on exact coordinate equality.

From the repository root, install the plotting option and run:

```bash
python -m pip install -e ".[plot]"
spinmdkit plot-layer examples/top_layer_moments/trajectory.xyz \
  --frame -1 --species U --axis z --layer top \
  --arrow-scale 1.0 --position-unit "Å" --moment-unit "μB" \
  --output examples/top_layer_moments/output/top_layer_moments.svg
```

![Top U-layer magnetic-moment arrows and xy projection](output/top_layer_moments.png)

The one command writes an editable SVG, a vector PDF, and a PNG preview with the
same base name. The SVG is the primary source for later editing.

The left panel preserves the full three-dimensional moment direction. The right
panel is the matching in-plane projection: because this command selects a z
layer, it plots xy positions and only `(mx, my)`. Its arrow length and color are
controlled by the projected magnitude, and the color bar states its numerical
range. The reported arrow scale applies to both panels, and all nine selected
atoms are shown.

The same rule applies to the other layer normals: `--axis x` adds a yz
projection using only `(my, mz)`, while `--axis y` adds an xz projection using
only `(mx, mz)`.

For a known layer position, replace automatic edge detection with an explicit
coordinate and tolerance:

```bash
spinmdkit plot-layer examples/top_layer_moments/trajectory.xyz \
  --frame -1 --species U --axis z \
  --coordinate 4.0 --tolerance 0.08 \
  --arrow-scale 1.0 --position-unit "Å" --moment-unit "μB" \
  --output examples/top_layer_moments/output/top_layer_moments.svg
```

The explicit selection includes atoms satisfying `|z - 4.0| <= 0.08` in the
source position unit. SpinMDKit reports the selected atom count, actual z range,
selection mode, full local-moment range, and in-plane moment range in the
terminal.

If automatic edge detection would return only one atom, the command stops and
asks for an explicit `--tolerance`; it does not silently treat one outlier as an
atomic plane.
