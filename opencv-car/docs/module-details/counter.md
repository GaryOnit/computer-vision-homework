---
topic: counter.py 虚拟线计数模块
keywords: [counter, line counter, 穿越检测, 冷却防抖, upward_ids]
triggers: [计数逻辑在哪, 为什么会重复计数, 上行判定规则]
confidence: L1
source: utils/counter.py
updated: 2026-06-10
---

# counter.py (`utils/counter.py`)

- `LineCounter` 负责虚拟线计数。
- `update(tracks)` 同时做三件事：
  1) 维护 `upward_ids`（本帧上行车辆）
  2) 判断是否穿越计数线
  3) 应用冷却防抖

## 判定规则

- 上行方向：`cy < prev_cy`
- 穿越计数：`cy <= line_y < prev_cy` 且不在冷却中

## 状态字段

- `_prev_y`: 上一帧中心点
- `_cooldown`: 冷却剩余帧
- `upward_ids`: 本帧用于可视化过滤的 ID 集合
