---
topic: 已知坑与反直觉行为
keywords: [踩坑, 计数方向, 防抖, 编解码器, MPS, 慢放]
triggers: [有什么坑, 为什么不计数, 输出视频异常, 追踪不稳定]
confidence: L1
source: app.py, models/tracker.py, utils/counter.py, utils/visualizer.py, utils/config.py
updated: 2026-06-10
---

# 已知坑与特殊约定

## 1) 计数方向容易写反

上行车辆在画面中是 y 坐标减小，正确穿越条件：

```python
cy <= self.line_y < prev_cy
```

## 2) 防抖依赖冷却帧

同一 `track_id` 计数后会进入冷却，避免边缘抖动重复计数。冷却帧数来自 `COOLDOWN_FRAMES`。

## 3) 只绘制上行车辆不是检测漏检

`Visualizer.draw()` 使用 `upward_ids` 过滤，只显示当前帧方向向上的目标；其余目标是被过滤，不是模型没检测到。

## 4) 输出视频慢放是“每帧写两次”

不是改 FPS 元数据，而是在主循环中连续 `writer.write(vis_frame)` 两次。

## 5) 编解码器需回退

不同平台对 `avc1` 支持不同，代码已内置 `avc1 -> mp4v -> MJPG` 回退链。

## 6) MPS 可用也可能失败

设备选择会先尝试 MPS，再回退 CPU；如果 MPS 运行时异常，可强制改为 CPU。
