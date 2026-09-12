<p align="center">
  <a href="README.md">English</a> | <strong>简体中文</strong>
</p>

# 磁矩时间演化

这个示例将一个多帧 Extended XYZ 轨迹转换为数值 CSV 和横向双面板图。输入是
特意构造的小型合成轨迹，因此可以快速检查完整命令。

在仓库根目录安装绘图依赖并运行：

```bash
python -m pip install -e ".[plot]"
spinmdkit plot-moments examples/moment_time_evolution/trajectory.xyz \
  --species U --timestep 0.001 --sample-every 100 \
  --time-offset 0.2 --time-unit ps --moment-unit "μB" \
  --output examples/moment_time_evolution/output/moment_time_evolution.png
```

这一条分析命令会同时生成：

- `output/moment_time_evolution.csv`：帧编号、物理时间、选中原子数、净
  `Mx/My/Mz/|M|`，以及局域磁矩模长的平均值、最小值和最大值。
- `output/moment_time_evolution.png`：左图显示净磁矩，右图显示局域磁矩模长统计。

![横向双面板磁矩时间演化图](output/moment_time_evolution.png)

对于上面的命令，相邻已保存帧之间包含 100 个 MD 积分步，每步为 0.001 ps；
0.2 ps 的偏移量用于补偿之前的一段时间。因此：

```text
time = 0.2 ps + frame_index * 0.001 ps * 100
```

`--sample-every` 描述轨迹的写出间隔，不会在分析过程中跳过数据。如果只想分析
每 N 个已保存帧中的一帧，可另外使用 `--frame-stride N`；计算时间仍使用原始
帧编号。

如果轨迹已经包含数值型帧级时间，请显式使用该值：

```bash
spinmdkit plot-moments trajectory.xyz --species U \
  --time-source metadata --time-key Time --time-scale 0.001 \
  --time-offset 0.0 --time-unit ps --moment-unit "μB" \
  --output moment_time_evolution.png
```

各项定义保持明确：

```text
M(t)             = sum_i s_i(t)
|M(t)|           = norm(M(t))
local mean(t)    = mean_i norm(s_i(t))
local minimum(t) = min_i norm(s_i(t))
local maximum(t) = max_i norm(s_i(t))
```

求和与局域统计只包含由 `--species` 选中的原子。单位只是用户提供的标签；
SpinMDKit 不会静默换算轨迹中的数值。
