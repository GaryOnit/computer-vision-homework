---
topic: opencv-car 知识库入口与检索范围
keywords: [opencv-car, 车辆计数, YOLOv8, ByteTrack, 文档索引, 知识库]
triggers: [查看文档目录, 项目知识库, 从哪里开始看代码]
confidence: L1
source: app.py, utils/config.py, models/tracker.py, utils/counter.py, utils/visualizer.py, models/detector.py
updated: 2026-06-10
---

# opencv-car 知识库

> 项目是一个离线车流量计数系统：读取本地视频，基于 YOLOv8 + ByteTrack 做车辆检测追踪，通过虚拟线统计上行车辆数量，并导出标注视频。

## 文档目录

| 优先级 | 文件 | 用途 |
|--------|------|------|
| P0 | `docs/quick-lookup.md` | 业务场景到代码路径速查 |
| P0 | `docs/architecture.md` | 模块架构与主流程 |
| P0 | `docs/file-index.md` | 全量文件索引 |
| P1 | `docs/implicit-knowledge.md` | 已知坑与反直觉行为 |
| P2 | `docs/module-details/app.md` | 入口与主循环细节 |
| P2 | `docs/module-details/config.md` | 全局配置项说明 |
| P2 | `docs/module-details/detector.md` | YOLO 单帧检测模块说明 |
| P2 | `docs/module-details/tracker.md` | YOLO + ByteTrack 追踪模块说明 |
| P2 | `docs/module-details/counter.md` | 虚拟线计数规则说明 |
| P2 | `docs/module-details/visualizer.md` | 绘制叠加模块说明 |
## 可检索信息范围

| 层级 | 来源 | 状态 | 可信度 |
|------|------|------|--------|
| 代码层 | `app.py`, `models/*.py`, `utils/*.py` | ✅ 已收录 | L1 |
| 变更历史层 | Git 提交历史 | ❌ 未收录 | - |
| 需求/任务层 | ONES | ❌ 未收录 | - |
| 文档层 | 无外部文档源 | ❌ 未收录 | - |
| 开发者输入层 | 当前会话沉淀 | ✅ 已收录 | L3 |

## 快速运行

```bash
cd /Users/megumi/Desktop/code/computer-vision/opencv-car
source .venv/bin/activate
python app.py --no-preview
```

默认输入 `vehicle.mp4`，默认输出 `output_videos/output_counted.mp4`。
