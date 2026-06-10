---
topic: tracker.py 追踪模块
keywords: [tracker, ByteTrack, persist, track_id, YOLO]
triggers: [追踪逻辑在哪, track_id怎么来的, bytetrack配置]
confidence: L1
source: models/tracker.py
updated: 2026-06-10
---

# tracker.py (`models/tracker.py`)

- 封装 YOLOv8 + ByteTrack 多目标追踪。
- `Tracker.update(frame)` 内部调用 `model.track(...)`。
- 关键参数：
  - `tracker=TRACKER`（默认 `bytetrack.yaml`）
  - `persist=True` 保持跨帧 ID 连续
  - `classes=VEHICLE_CLASSES` 仅过滤车辆
- 返回 `results[0]`，供计数与绘制模块消费。
