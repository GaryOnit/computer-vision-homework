---
topic: 全量文件路径索引
keywords: [文件列表, 文件索引, 目录结构, 所有文件]
triggers: [项目有哪些文件, 文件在哪, 目录结构]
confidence: L1
source: 仓库根目录扫描
updated: 2026-06-09
---

# 全量文件索引

## 项目目录结构

```
opencv-people/
├── app.py                          # Streamlit Web 应用入口（主程序）
├── models/
│   ├── __init__.py                 # 模块初始化
│   └── deeplabv3.py                # DeepLabV3Segmenter 类（模型核心）
├── utils/
│   ├── __init__.py                 # 模块初始化
│   ├── segment.py                  # PortraitSegmenter 封装类
│   └── visualize.py                # 可视化工具函数
└── docs/                           # AI 知识库
    ├── README.md                   # 知识库目录与范围
    ├── quick-lookup.md             # 场景速查表
    ├── architecture.md             # 系统架构
    ├── file-index.md               # 本文件
    ├── implicit-knowledge.md       # 踩坑与特殊设计
    └── module-details/
        ├── deeplabv3.md            # DeepLabV3 模块详情
        ├── portrait-segmenter.md   # PortraitSegmenter 模块详情
        ├── app-ui.md               # Streamlit UI 层详情
        └── visualize.md            # 可视化工具详情
```

## 文件详细说明

| 路径 | 类型 | 大小估计 | 核心职责 |
|------|------|---------|---------|
| `app.py` | Python | ~245 行 | Streamlit 页面主逻辑，含单图处理+批量处理 |
| `models/__init__.py` | Python | 空 | 使 models 成为 Python 包 |
| `models/deeplabv3.py` | Python | ~105 行 | DeepLabV3 模型加载/推理/前后处理 |
| `utils/__init__.py` | Python | 空 | 使 utils 成为 Python 包 |
| `utils/segment.py` | Python | ~54 行 | 高层封装，提供文件路径接口 |
| `utils/visualize.py` | Python | ~50 行 | matplotlib 可视化工具，独立于 UI |

## 运行时临时文件（不入库）

| 路径 | 生成时机 | 说明 |
|------|---------|------|
| `temp_result.png` | 单图透明背景下载时 | 用完即删（`os.remove`） |
| `temp_result.jpg` | 单图有色背景下载时 | 用完即删 |
| `temp_mask.png` | 下载掩码时 | 用完即删 |
| `batch_results/` | 批量处理时 | 临时存放结果，打包后不自动删除 |
| `batch_results.zip` | 批量处理完成后 | 供下载 |
