# AGENTS.md — opencv-people AI 编码指南

> 本文件供 AI Agent 阅读，指导代码修改、问题排查和功能扩展。

---

## 项目简介

**opencv-people** 是一个基于 DeepLabV3 的命令行人像分割工具。
核心能力：输入本地图片路径，输出透明背景人像 PNG。

**启动命令**：
```bash
cd /Users/megumi/Desktop/code/computer-vision/opencv-people
./venv/bin/python app.py people.jpg
```

如果在 macOS + Homebrew Python 环境遇到 `pyexpat` 相关动态库问题，使用：
```bash
DYLD_LIBRARY_PATH=/opt/homebrew/lib ./venv/bin/python app.py people.jpg
```

---

## 可检索信息范围

| 层级 | 来源 | 可信度 |
|------|------|--------|
| 代码层（L1） | `app.py`, `models/deeplabv3.py`, `utils/segment.py`, `utils/visualize.py` | 最高，以代码为准 |
| 对话沉淀（L3） | `docs/implicit-knowledge.md` | 辅助参考 |
| 变更历史、需求文档 | 未收录 | - |

**冲突原则**：代码内容（L1）> 任何文档描述，文档若与代码冲突请标注 `[⚠️ 可能过时，以代码为准]`。

---

## 知识库文档路径（AI 加载优先级）

### P0 必读（定位代码时先看这里）

- [`docs/quick-lookup.md`](docs/quick-lookup.md) — 业务场景 → 代码路径速查表 + 术语表
- [`docs/architecture.md`](docs/architecture.md) — 系统架构、模块依赖、调用流程
- [`docs/file-index.md`](docs/file-index.md) — 全量文件索引与目录结构

### P1 按需（排查问题、写新功能时看）

- [`docs/implicit-knowledge.md`](docs/implicit-knowledge.md) — 踩坑与特殊约定

### P2 参考（深入了解某个模块时看）

- [`docs/module-details/deeplabv3.md`](docs/module-details/deeplabv3.md) — DeepLabV3Segmenter 类详解
- [`docs/module-details/portrait-segmenter.md`](docs/module-details/portrait-segmenter.md) — PortraitSegmenter 封装层详解
- [`docs/module-details/app-ui.md`](docs/module-details/app-ui.md) — `app.py` 命令行入口详解
- [`docs/module-details/visualize.md`](docs/module-details/visualize.md) — 可视化工具详解

---

## 已知坑速查（高频，必须记住）

| # | 坑 | 正确做法 |
|---|-----|---------|
| 1 | 访问底层模型时是双层 `.segmenter` | `segmenter.segmenter.segment(image)` |
| 2 | OpenCV 默认是 BGR，直接显示会偏色 | 展示前做 `BGR->RGB` 转换 |
| 3 | 首次运行会下载模型权重 | 需联网，或预先缓存模型 |
| 4 | `app.py` 默认输出覆盖同名目标文件 | 使用 `-o` 指定输出文件 |

---

## 项目目录结构

```
opencv-people/
├── app.py                      # 命令行入口（主程序）
├── models/
│   ├── __init__.py
│   └── deeplabv3.py            # DeepLabV3Segmenter（模型核心）
├── utils/
│   ├── __init__.py
│   ├── segment.py              # PortraitSegmenter（封装层）
│   └── visualize.py            # 可视化工具（离线）
└── docs/                       # 本知识库
```

---

## 编码约束

1. **图像格式**：项目内部统一使用 BGR（OpenCV 原生），仅在展示时转换
2. **掩码格式**：`uint8` numpy 数组，255 = 人像区域，0 = 背景
3. **设备默认值**：`device='cpu'`
4. **入口职责**：`app.py` 只做参数解析、I/O、主流程串联；分割逻辑在 `models/` 与 `utils/`

---

## 信息可信度分级

| 级别 | 来源 | 说明 |
|------|------|------|
| L1 | 代码文件 | 最高可信度，实际执行的逻辑 |
| L2 | 设计文档/需求文档 | 中等可信度（本项目暂无） |
| L3 | 对话沉淀/开发者口述 | 辅助参考，可能不完整 |
