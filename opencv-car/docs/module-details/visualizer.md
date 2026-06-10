---
topic: visualizer.py 绘制模块
keywords: [visualizer, draw, 边界框, 计数线, HUD]
triggers: [画框在哪实现, 如何只画上行车辆, 看板怎么绘制]
confidence: L1
source: utils/visualizer.py
updated: 2026-06-10
---

# visualizer.py (`utils/visualizer.py`)

- `Visualizer.draw(frame, tracks, count, upward_ids)` 负责所有叠加绘制。
- 绘制顺序：
  1) 计数线
  2) 车辆框 + Track ID（可按 `upward_ids` 过滤）
  3) 左上角半透明计数看板
- 函数内部对 `frame.copy()` 操作，不修改原始帧。
