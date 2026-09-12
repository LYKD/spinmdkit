<p align="center">
  <img src="docs/assets/spinmdkit-lockup.png" alt="SpinMDKit 标志" width="720">
</p>

<p align="center">
  <a href="README.md">English</a> | <strong>简体中文</strong>
</p>

# SpinMDKit

[![CI](https://github.com/LYKD/spinmdkit/actions/workflows/ci.yml/badge.svg)](https://github.com/LYKD/spinmdkit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**SpinMDKit 是面向自旋分子动力学、格式可扩展的磁矩后处理框架。**
它能够以流式方式读取大型轨迹、计算磁学观测量、导出可直接分析的时间序列，
并绘制三维自旋矢量，内置支持 Extended XYZ 轨迹。

项目底层有意保持精简：一个定义明确的帧数据模型、一个由格式模式驱动的流式
读取器、一套经过测试的 Python API/CLI，以及可选的 C++17 加速内核。
版本 1.0.0 确立了可下载工具包的稳定基础；以后增加其他模拟格式时，不需要修改
数据层、分析层或可视化层。

## 安装

从 [Releases 页面](https://github.com/LYKD/spinmdkit/releases)下载对应平台的
wheel，然后使用 pip 安装：

```bash
python -m pip install spinmdkit-1.0.0-...whl
```

基础安装只有一个运行依赖：**NumPy**。绘图功能作为独立的可选依赖安装：

```bash
python -m pip install "spinmdkit[plot]"
```

也可以从源码编译 C++17 扩展：

```bash
git clone https://github.com/LYKD/spinmdkit.git
cd spinmdkit
python -m pip install ".[test]"
python -m pytest
```

从源码构建需要 C++17 编译器。在受限环境中，可以关闭原生模块并构建仅使用
NumPy 的版本：

```bash
SPINMDKIT_DISABLE_NATIVE=1 python -m pip install .
```

在 PowerShell 中，请先执行
`$env:SPINMDKIT_DISABLE_NATIVE='1'`，再运行 pip。原生扩展是可选的；即使编译
失败，也不会阻止 NumPy 实现被安装。

## 快速开始

以流式方式检查 GPUMD 轨迹，不把整个文件一次性载入内存：

```bash
spinmdkit inspect trajectory.xyz --species U
```

输入格式可以根据文件后缀自动选择，也可以显式指定：

```bash
spinmdkit formats
spinmdkit inspect trajectory.xyz --format extxyz --species U
```

导出净磁矩、局域磁矩模长、磁力模长和派生的 `spin x mforce` 力矩模长：

```bash
spinmdkit timeseries trajectory.xyz -o magnetic-timeseries.csv --species U
```

用一个命令导出数值数据，并绘制净 `Mx/My/Mz/|M|` 与局域磁矩模长的
平均值、最小值和最大值：

```bash
spinmdkit plot-moments trajectory.xyz --species U \
  --timestep 0.001 --sample-every 100 --time-offset 0.2 \
  --time-unit ps --moment-unit "μB" -o moment_time_evolution.png
```

该命令会在横排双面板 PNG 旁生成 `moment_time_evolution.csv`。
`--sample-every` 表示轨迹每隔多少个 MD 积分步保存一帧；如果还需要在后处理中
降低采样密度，可以使用 `--frame-stride`。当帧元数据本身已经包含时间时，使用
`--time-source metadata --time-key Time` 显式读取。

对于反铁磁体系，必须显式提供子晶格符号。当模式长度能够整除所选原子数时，
该模式才会在所选原子上重复：

```bash
spinmdkit timeseries trajectory.xyz -o afm.csv \
  --species U --sublattice-pattern "+--+"
```

将某一帧绘制成三维彩色箭头：

```bash
spinmdkit plot-frame trajectory.xyz -o frame-0.png \
  --frame 0 --species U --normalize
```

从最后一帧选择完整的顶层 U 原子，并把三维磁矩视图与面内投影横向排列；箭头按
磁矩大小缩放，右侧色标给出数值范围：

```bash
spinmdkit plot-layer examples/top_layer_moments/trajectory.xyz \
  --frame -1 --species U --axis z --layer top \
  --arrow-scale 1.0 --position-unit "Å" --moment-unit "μB" \
  -o top_layer_moments.svg
```

自动边界层识别会根据坐标间隔聚合出一个原子面，而不是只保留坐标恰好最大的
单个原子。对于已知位置的面，也可以使用
`--coordinate Z --tolerance DZ` 显式选择。投影会跟随选层法向：x 层使用 yz
坐标及 `(my, mz)`，y 层使用 xz 坐标及 `(mx, mz)`，z 层使用 xy 坐标及
`(mx, my)`。完整说明见双语
[`top_layer_moments` 案例](examples/top_layer_moments/README.zh-CN.md)。

每个完整示例都放在独立目录中。时间轴、CSV 和横排双图的完整流程见
[`examples/moment_time_evolution`](examples/moment_time_evolution/README.zh-CN.md)。
八原子反铁磁示例可以这样检查：

```bash
spinmdkit inspect examples/afm_frame/trajectory.xyz --species U \
  --sublattice-pattern "+--+" --json
```

## Python API

```python
from spinmdkit import iter_extxyz, summarize_frame

for frame in iter_extxyz("trajectory.xyz"):
    result = summarize_frame(frame, species="U")
    print(result["magnetization"], result["mean_moment_norm"])
```

每个 `Frame` 都包含 `species`、`positions`、可选的 `cell`、未经修改的帧级
`metadata`，以及按名称保存的逐原子 `properties`。读取器支持任意 Extended XYZ
属性模式，包括 `spin`、`mforce` 和 `spin_velocity`，也支持 `.xyz.gz` 压缩流。

## 模块边界

```text
spinmdkit.data           经过验证的帧对象；不包含文件或绘图逻辑
spinmdkit.io             读取器协议、格式注册表和轨迹访问
spinmdkit.io.readers     相互隔离的输入格式适配器，包括 Extended XYZ
spinmdkit.analysis       物理观测量、空间选择和帧级汇总
spinmdkit.kernels        NumPy/原生计算后端边界
spinmdkit.export         低依赖 CSV 序列化
spinmdkit.visualization  可选绘图层；仅在需要时导入 Matplotlib
spinmdkit.cli            只负责组合上述功能的轻量命令层
```

依赖关系保持单向。`io` 不会反向导入分析或绘图逻辑，`analysis` 也不会导入 CLI
或 Matplotlib。因此，格式适配器、物理观测量和绘图器都可以独立测试与调试。

新格式只需要实现小型 `TrajectoryReader` 协议，声明名称和文件后缀并完成注册。
所有适配器都会生成同一种与格式无关的 `Frame`，使下游分析和绘图不依赖输入
文件的具体语法。

## 科学约定

- `spin` 是直接从轨迹读取的局域磁矩矢量。
- `mforce` 始终作为独立命名的类磁力输出保存。
- 力矩是按 `spin x mforce` 计算的派生量，不会被当作独立标签。
- 只有在明确提供 `+1/-1` 子晶格符号后才计算 Néel 矢量。
- `stress`、`virial`、单位和符号约定按源数据保存，SpinMDKit 不会静默换算。
- 数值会保留其来源信息，不会被重新表述为参考数据。

设计细节见[数据模型](docs/data-model.md)、[架构](docs/architecture.md)和
[新增读取器](docs/adding-readers.md)。

## 版本策略

只有在维护者明确要求时才修改版本号。提交代码、调试、运行 CI 或增加功能都不会
自动提升版本。详细规则见 [VERSIONING.md](VERSIONING.md)。

## 当前命令界面

| 命令 | 用途 |
| --- | --- |
| `spinmdkit formats` | 列出当前注册的输入格式适配器 |
| `spinmdkit inspect` | 以流式方式检查轨迹结构和数值范围 |
| `spinmdkit timeseries` | 将逐帧磁学观测量导出为 CSV |
| `spinmdkit plot-moments` | 导出 CSV 并绘制横向双面板磁矩时间演化图 |
| `spinmdkit plot-frame` | 绘制某一帧的静态三维自旋矢量图 |
| `spinmdkit plot-layer` | 选择一个原子层并绘制按磁矩大小缩放的箭头图 |

## 路线图

1. 通过独立适配器支持更多模拟格式和轨迹写出格式。
2. 增加更多空间分辨、子晶格分辨和温度分辨的磁学观测量。
3. 建立交互式与批处理可视化流程。
4. 为领域专用分析提供稳定的插件接口。
5. 增加基准测试和适用于生产轨迹的可扩展并行读取器。

欢迎提交贡献和可复现测试用例。详情见 [CONTRIBUTING.md](CONTRIBUTING.md)。
