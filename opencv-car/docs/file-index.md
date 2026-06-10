---
topic: 仓库文件索引
keywords: [文件索引, 目录结构, 文件清单, opencv-car]
triggers: [项目有哪些文件, 全量目录, 文件在哪]
confidence: L1
source: 仓库目录扫描
updated: 2026-06-10
---

# 文件索引

```text
opencv-car/
├── AGENTS.md
├── requirements.txt
├── vehicle.mp4
├── yolov8n.pt
├── app.py
├── models/
│   ├── __init__.py
│   ├── detector.py
│   └── tracker.py
├── utils/
│   ├── __init__.py
│   ├── config.py
│   ├── counter.py
│   └── visualizer.py
├── output_videos/
│   └── output_counted.mp4
├── docs/
│   ├── README.md
│   ├── quick-lookup.md
│   ├── architecture.md
│   ├── file-index.md
│   ├── implicit-knowledge.md
│   └── module-details/
│       ├── app.md
│       ├── config.md
│       ├── detector.md
│       ├── tracker.md
│       ├── counter.md
│       └── visualizer.md
├── .catpaw/
│   ├── memory/
│   └── skills/
└── .claude/

```

## 说明

- `output_videos/`、`*.pt`、`.catpaw/` 在 `.gitignore` 中被忽略。
- 目录结构已和 `opencv-people` 对齐为 `app.py + models/ + utils/ + docs/`。
