---
topic: 系统架构、模块依赖与处理流程
keywords: [架构, 模块依赖, 流程, 分层, CLI, DeepLabV3, PortraitSegmenter]
triggers: [系统怎么设计的, 模块关系, 调用流程, 整体架构]
confidence: L1
source: app.py, utils/segment.py, models/deeplabv3.py
updated: 2026-06-09
---

# 系统架构

## 分层架构

```
┌─────────────────────────────────────────┐
│             入口层 (CLI)                 │
│   app.py  — 命令行入口                   │
│   · 参数解析（input/output）              │
│   · 文件读取与输出路径处理                │
│   · 串联分割流程                          │
└────────────────────┬────────────────────┘
                     │ 调用
┌────────────────────▼────────────────────┐
│            业务封装层 (Utils)            │
│   utils/segment.py — PortraitSegmenter  │
│   · 封装底层模型                          │
│   · 提供文件路径级别接口                  │
└────────────────────┬────────────────────┘
                     │ 调用
┌────────────────────▼────────────────────┐
│              模型层 (Models)             │
│   models/deeplabv3.py                    │
│   — DeepLabV3Segmenter                   │
│   · preprocess: BGR→RGB→Tensor→归一化    │
│   · 推理：torch.no_grad()                │
│   · postprocess: 提取 COCO 类别 15 掩码  │
└────────────────────┬────────────────────┘
                     │ 调用
┌────────────────────▼────────────────────┐
│           第三方依赖 (External)           │
│   torchvision.models.segmentation       │
│   .deeplabv3_resnet50(pretrained=True)  │
└─────────────────────────────────────────┘
```

---

## 核心类/函数一览

| 模块 | 类/函数 | 职责 |
|------|---------|------|
| `app.py` | `build_parser()` | 定义命令行参数 |
| `app.py` | `main()` | I/O 处理与流程编排 |
| `models/deeplabv3.py` | `DeepLabV3Segmenter` | 模型加载、推理、前后处理 |
| `models/deeplabv3.py` | `DeepLabV3Segmenter.segment(image)` | 输入 BGR numpy 图，输出二值掩码 |
| `models/deeplabv3.py` | `DeepLabV3Segmenter.extract_portrait()` | 输出带 Alpha 通道 BGRA 图 |
| `utils/segment.py` | `PortraitSegmenter` | 上层封装，持有 `self.segmenter` |
| `utils/segment.py` | `PortraitSegmenter.segment_image()` | 文件路径 → 掩码 + 结果图 |

---

## 单张图片分割流程

```
命令行传入 input 路径
      │
      ▼
app.py: cv2.imread 读取 BGR 图像
      │
      ▼
app.py: PortraitSegmenter(device='cpu')
      │
      ▼
app.py: segmenter.segmenter.segment(image)
      │
      ▼
DeepLabV3Segmenter:
  preprocess -> model inference -> postprocess
      │
      ▼
app.py: segmenter.segmenter.extract_portrait(image, mask)
      │
      ▼
写入 <input_stem>_portrait.png 或 -o 指定路径
```
