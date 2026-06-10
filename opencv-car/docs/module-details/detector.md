---
topic: detector.py 单帧检测模块
keywords: [detector, YOLO, predict, 单帧检测]
triggers: [单帧检测怎么做, detector用途]
confidence: L1
source: models/detector.py
updated: 2026-06-10
---

# detector.py (`models/detector.py`)

- 主要用于单帧检测调试。
- `Detector.detect(frame)` 调用 `model.predict(...)`。
- 仅返回车辆类别，阈值与类别从 `config.py` 读取。
- 设备选择策略：优先 MPS，不可用则 CPU。
