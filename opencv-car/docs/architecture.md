---
topic: 系统架构与处理流程
keywords: [架构, 处理流程, YOLOv8, ByteTrack, OpenCV, 计数线]
triggers: [系统怎么工作, 模块关系, 端到端流程]
confidence: L1
source: app.py, utils/config.py, models/tracker.py, utils/counter.py, utils/visualizer.py
updated: 2026-06-10
---

# 系统架构

## 分层结构

1. 入口层：`app.py`
2. 能力层：`models/tracker.py`、`utils/counter.py`、`utils/visualizer.py`
3. 配置层：`utils/config.py`
4. 依赖层：Ultralytics、OpenCV、NumPy、PyTorch

## 主流程

```text
读取视频帧 -> Tracker.update(frame)
          -> LineCounter.update(tracks)
          -> Visualizer.draw(frame, tracks, count, upward_ids)
          -> VideoWriter 输出
```

## 关键设计点

- 追踪状态持久化：`persist=True`，保证 Track ID 跨帧连续。
- 计数方向：只统计上行穿越，条件是 `cy <= line_y < prev_cy`。
- 防抖机制：每个 `track_id` 有冷却帧，避免抖动重复计数。
- 输出兼容：`avc1 -> mp4v -> MJPG` 多编解码器回退。
- 慢放策略：每帧写入两次，实现 0.5x 效果。
