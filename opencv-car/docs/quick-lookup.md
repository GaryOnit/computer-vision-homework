---
topic: 业务场景到代码定位速查
keywords: [速查, 代码定位, 车辆计数, 追踪, 虚拟线, 输出视频]
triggers: [哪个文件负责什么, 快速定位功能, 改某个功能去哪里]
confidence: L1
source: app.py, utils/config.py, models/tracker.py, utils/counter.py, utils/visualizer.py, models/detector.py
updated: 2026-06-10
---

# 业务场景速查

| 场景 | 文件 | 关键函数/类 |
|------|------|-------------|
| 启动程序与参数解析 | `app.py` | `parse_args()`, `main()` |
| 视频写出编解码器回退 | `app.py` | `get_video_writer()` |
| 修改默认输入输出路径 | `utils/config.py` | `INPUT_VIDEO`, `OUTPUT_VIDEO` |
| 调整检测阈值/车辆类别 | `utils/config.py` | `CONF_THRESHOLD`, `VEHICLE_CLASSES` |
| YOLO 检测 + ByteTrack 追踪 | `models/tracker.py` | `Tracker.update()` |
| 单帧检测调试 | `models/detector.py` | `Detector.detect()` |
| 穿越虚拟线计数 | `utils/counter.py` | `LineCounter.update()` |
| 只绘制上行车辆 | `utils/visualizer.py` | `Visualizer.draw(..., upward_ids=...)` |
| 调整计数线位置 | `utils/config.py`, `app.py` | `COUNTING_LINE_Y_RATIO`, `line_y` |
| 调整可视化颜色/字体 | `utils/config.py` | `BOX_COLOR`, `LINE_COLOR`, `FONT_SCALE` |

## 常用命令

```bash
# 默认运行（显示预览）
python app.py

# 无头运行（服务器/远程环境推荐）
python app.py --no-preview

# 指定输入输出
python app.py --input vehicle.mp4 --output output_videos/custom.mp4
```
