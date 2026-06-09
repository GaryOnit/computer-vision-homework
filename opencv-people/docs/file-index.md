---
topic: 全量文件路径索引
keywords: [文件列表, 文件索引, 目录结构, 所有文件, CLI]
triggers: [项目有哪些文件, 文件在哪, 目录结构]
confidence: L1
source: 仓库根目录扫描
updated: 2026-06-09
---

# 全量文件索引

## 项目目录结构

```
opencv-people/
├── app.py                          # 命令行入口（主程序）
├── requirements.txt                # 运行依赖
├── models/
│   ├── __init__.py                 # 模块初始化
│   └── deeplabv3.py                # DeepLabV3Segmenter 类（模型核心）
├── utils/
│   ├── __init__.py                 # 模块初始化
│   ├── segment.py                  # PortraitSegmenter 封装类
│   └── visualize.py                # 可视化工具函数（离线）
└── docs/                           # AI 知识库
    ├── README.md                   # 知识库目录与范围
    ├── quick-lookup.md             # 场景速查表
    ├── architecture.md             # 系统架构
    ├── file-index.md               # 本文件
    ├── implicit-knowledge.md       # 踩坑与特殊设计
    └── module-details/
        ├── deeplabv3.md            # DeepLabV3 模块详情
        ├── portrait-segmenter.md   # PortraitSegmenter 模块详情
        ├── app-ui.md               # app.py 命令行入口详情
        └── visualize.md            # 可视化工具详情
```

## 文件详细说明

| 路径 | 类型 | 大小估计 | 核心职责 |
|------|------|---------|---------|
| `app.py` | Python | ~40 行 | 命令行参数解析 + 单图分割主流程 |
| `requirements.txt` | Text | ~4 行 | 运行依赖 |
| `models/__init__.py` | Python | 空 | 使 models 成为 Python 包 |
| `models/deeplabv3.py` | Python | ~105 行 | DeepLabV3 模型加载/推理/前后处理 |
| `utils/__init__.py` | Python | 空 | 使 utils 成为 Python 包 |
| `utils/segment.py` | Python | ~54 行 | 高层封装，提供文件路径接口 |
| `utils/visualize.py` | Python | ~50 行 | matplotlib 可视化工具，独立于主流程 |
