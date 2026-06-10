# AGENTS.md — opencv-car AI 编码指南

> 本文件供 AI Agent 阅读，指导代码修改、问题排查和功能扩展。

## 项目简介

`opencv-car` 是一个基于 YOLOv8 + ByteTrack 的离线车流量计数项目。
输入本地视频，输出带检测框、轨迹 ID 与计数看板的标注视频。

## 可检索信息范围

| 层级 | 来源 | 可信度 |
|------|------|--------|
| 代码层（L1） | `app.py`, `utils/config.py`, `models/tracker.py`, `utils/counter.py`, `utils/visualizer.py`, `models/detector.py` | 最高，以代码为准 |
| 文档层（L2） | 未收录 | - |
| 对话沉淀（L3） | `docs/implicit-knowledge.md` | 辅助参考 |

冲突原则：L1 > L2 > L3。

## 知识库路径（加载优先级）

### P0 必读

- `docs/README.md`
- `docs/quick-lookup.md`
- `docs/architecture.md`
- `docs/file-index.md`

### P1 按需

- `docs/implicit-knowledge.md`

### P2 参考

- `docs/module-details/app.md`
- `docs/module-details/config.md`
- `docs/module-details/detector.md`
- `docs/module-details/tracker.md`
- `docs/module-details/counter.md`
- `docs/module-details/visualizer.md`
## 已知坑速查

1. 计数方向是 y 减小方向，上行穿越条件为 `cy <= line_y < prev_cy`。
2. `Visualizer.draw()` 可能按 `upward_ids` 过滤，不显示并不等于没检测到。
3. 慢放通过每帧写两次实现，不是改 FPS 元数据。
4. 编解码器必须有回退链：`avc1 -> mp4v -> MJPG`。
5. MPS 可用不代表稳定，必要时回退 CPU。

## 编码约束

1. 参数统一从 `utils/config.py` 读取，避免业务代码硬编码。
2. 保持模块职责单一：检测/追踪/计数/绘制分层不混写。
3. 修改计数逻辑时必须同时检查 `upward_ids` 与防抖状态的一致性。
4. 可视化逻辑应继续在 `frame.copy()` 上作图，避免污染原帧。
5. 入口脚本必须兼容 `--no-preview` 无头运行。

## 快速运行

```bash
cd /Users/megumi/Desktop/code/computer-vision/opencv-car
source .venv/bin/activate
python app.py --no-preview
```
