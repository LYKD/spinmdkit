<p align="center">
  <a href="README.md">English</a> | <strong>简体中文</strong>
</p>

# 显式 AFM 帧示例

这个小型双帧轨迹演示物种选择和显式重复的 AFM 子晶格模式。

```bash
spinmdkit inspect examples/afm_frame/trajectory.xyz --species U \
  --sublattice-pattern "+--+" --json
```

子晶格模式只应用于选中的四个 U 原子。SpinMDKit 不会根据原子顺序自动推断
AFM 子晶格。
