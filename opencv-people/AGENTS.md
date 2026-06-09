# AGENTS.md — opencv-people AI 编码指南

> 本文件供 AI Agent 阅读，指导代码修改、问题排查和功能扩展。

---

## 项目简介

**opencv-people** 是一个基于 DeepLabV3 + Streamlit 的 AI 人像分割 Web 应用。
核心能力：上传人像照片 → 自动识别人像 → 背景替换/透明抠图/批量处理。

**启动命令**：
```bash
pip install streamlit opencv-python torch torchvision numpy matplotlib
streamlit run app.py
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

- [`docs/quick-lookup.md`](docs/quick-lookup.md) — 业务场景 → 代码路径速查 + 术语表
- [`docs/architecture.md`](docs/architecture.md) — 系统架构、模块依赖、完整请求流程
- [`docs/file-index.md`](docs/file-index.md) — 全量文件索引与目录结构

### P1 按需（排查问题、写新功能时看）

- [`docs/implicit-knowledge.md`](docs/implicit-knowledge.md) — **踩坑必读**，含 9 条特殊设计和已知坑

### P2 参考（深入了解某个模块时看）

- [`docs/module-details/deeplabv3.md`](docs/module-details/deeplabv3.md) — DeepLabV3Segmenter 类详解
- [`docs/module-details/portrait-segmenter.md`](docs/module-details/portrait-segmenter.md) — PortraitSegmenter 封装层详解
- [`docs/module-details/app-ui.md`](docs/module-details/app-ui.md) — Streamlit UI 层逻辑详解
- [`docs/module-details/visualize.md`](docs/module-details/visualize.md) — 可视化工具详解

---

## 已知坑速查（高频，必须记住）

| # | 坑 | 正确做法 |
|---|-----|---------|
| 1 | `app.py` 中访问模型要用 `segmenter.segmenter.xxx()`，双层 `.segmenter` | `PortraitSegmenter.segmenter` 才是 `DeepLabV3Segmenter` 实例 |
| 2 | OpenCV 图像是 BGR，传给 Streamlit 要转 RGB | `cv2.cvtColor(img, cv2.COLOR_BGR2RGB)` |
| 3 | `st.color_picker()` 返回 `"#RRGGBB"` 字符串，需手动解析为 BGR 元组 | 见 `app.py` 第 50-54 行 |
| 4 | 形态学处理被执行了两次（`postprocess` 内一次 + `app.py` 可选一次） | 如需精确控制，去掉 `postprocess` 内的形态学 |
| 5 | `batch_results/` 和 `batch_results.zip` 不自动清理 | 需手动删除 |
| 6 | `utils/visualize.py` 未被 `app.py` 引用，是离线脚本工具 | 不要在 UI 流程中期望它有效果 |

---

## 项目目录结构

```
opencv-people/
├── app.py                      # Web UI 入口（主程序）
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

1. **图像格式**：项目内部统一使用 BGR（OpenCV 原生），仅在展示/输出时转换
2. **掩码格式**：`uint8` numpy 数组，255 = 人像区域，0 = 背景
3. **设备默认值**：`device='cpu'`，生产部署若有 GPU 可改为 `'cuda'`
4. **模型只加载一次**：通过 `@st.cache_resource` 保证，不要在处理函数内重复初始化
5. **临时文件**：下载功能使用写文件+读取+删除的模式，路径相对于 `streamlit run` 的工作目录

---

## 信息可信度分级

| 级别 | 来源 | 说明 |
|------|------|------|
| L1 | 代码文件 | 最高可信度，实际执行的逻辑 |
| L2 | 设计文档/需求文档 | 中等可信度（本项目暂无） |
| L3 | 对话沉淀/开发者口述 | 辅助参考，可能不完整 |
