---
topic: app.py 入口与主循环
keywords: [app.py, 入口, argparse, 主循环, VideoWriter]
triggers: [程序入口在哪, 主流程怎么跑, 视频写出逻辑]
confidence: L1
source: app.py
updated: 2026-06-10
---

# app.py

- 负责参数解析：`--input`、`--output`、`--no-preview`。
- 打开视频后计算 `line_y = int(height * COUNTING_LINE_Y_RATIO)`。
- 初始化 `Tracker`、`LineCounter`、`Visualizer`。
- 每帧流程：追踪 -> 计数 -> 绘制 -> 写出。
- 每帧写两次用于 0.5x 慢放。
- 最终打印处理帧数、计数、输出路径。
