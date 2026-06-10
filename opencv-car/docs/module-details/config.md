---
topic: config.py 全局配置说明
keywords: [config, 配置, 阈值, 计数线, 可视化参数]
triggers: [参数在哪里改, 默认路径在哪, 阈值怎么调]
confidence: L1
source: utils/config.py
updated: 2026-06-10
---

# config.py (`utils/config.py`)

## 路径参数

- `INPUT_VIDEO`: 默认输入视频
- `OUTPUT_VIDEO`: 默认输出视频
- `MODEL_PATH`: YOLO 权重文件

## 检测参数

- `CONF_THRESHOLD`: 置信度阈值
- `IOU_THRESHOLD`: NMS IoU 阈值
- `VEHICLE_CLASSES`: 车辆类别（COCO ID）

## 计数参数

- `COUNTING_LINE_Y_RATIO`: 计数线位置（相对高度）
- `COOLDOWN_FRAMES`: 计数防抖冷却帧

## 可视化参数

- `SHOW_PREVIEW`, `BOX_COLOR`, `LINE_COLOR`, `TEXT_COLOR`
- `FONT_SCALE`, `THICKNESS`
