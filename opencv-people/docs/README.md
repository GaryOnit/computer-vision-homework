---
topic: 知识库目录与可检索信息范围
keywords: [知识库, 文档索引, docs, 人像分割系统, opencv-people]
triggers: [知识库总览, 文档目录, 从哪里找文档]
confidence: L1
source: docs/README.md
updated: 2026-06-09
---

# opencv-people 知识库

> **项目简介**：基于 DeepLabV3 + Streamlit 的 AI 人像分割 Web 应用，支持背景替换、透明抠图、批量处理。

---

## 文档目录

| 优先级 | 文件 | 描述 |
|--------|------|------|
| P0 | [quick-lookup.md](quick-lookup.md) | 业务场景→代码路径速查表 + 术语表 |
| P0 | [architecture.md](architecture.md) | 系统架构、模块依赖、请求流程 |
| P0 | [file-index.md](file-index.md) | 全量文件路径索引 |
| P1 | [implicit-knowledge.md](implicit-knowledge.md) | 已知坑、反直觉设计、特殊约定 |
| P2 | [module-details/deeplabv3.md](module-details/deeplabv3.md) | DeepLabV3 模型封装模块详细说明 |
| P2 | [module-details/portrait-segmenter.md](module-details/portrait-segmenter.md) | PortraitSegmenter 工具类详细说明 |
| P2 | [module-details/app-ui.md](module-details/app-ui.md) | Streamlit UI 层逻辑详细说明 |
| P2 | [module-details/visualize.md](module-details/visualize.md) | 可视化工具模块详细说明 |

---

## 可检索信息范围

| 层级 | 来源 | 状态 | 可信度 |
|------|------|------|--------|
| 代码层 | `app.py`, `models/deeplabv3.py`, `utils/segment.py`, `utils/visualize.py` | ✅ 全量收录 | L1 |
| 变更历史层 | Git 提交历史 | ❌ 未收录 | - |
| 需求/任务层 | 无 ONES 项目 | ❌ 未收录 | - |
| 文档层 | 无学城文档 | ❌ 未收录 | - |
| 开发者输入层 | 本知识库构建对话 | ✅ 已收录 | L3 |

**AI 搜索优先级**：P0 必读 → P1 按需 → P2 参考

---

## 启动方式

```bash
cd /path/to/opencv-people
pip install streamlit opencv-python torch torchvision numpy matplotlib
streamlit run app.py
```

浏览器访问 `http://localhost:8501`
