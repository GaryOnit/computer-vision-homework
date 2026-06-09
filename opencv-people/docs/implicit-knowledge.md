---
topic: 已知坑、反直觉设计与特殊约定
keywords: [踩坑, 注意事项, 坑, 特殊设计, 反直觉, 已知问题, BGR, 双层访问, CLI]
triggers: [有什么坑, 注意什么, 为什么这样写, 反直觉行为, 特殊约定]
confidence: L1
source: app.py, models/deeplabv3.py, utils/segment.py
updated: 2026-06-09
---

# 已知坑与特殊设计

## 1. 双层 `.segmenter` 访问（高频踩坑）

**现象**：`app.py` 中访问模型的方式是 `segmenter.segmenter.segment(image)`。

**原因**：`PortraitSegmenter` 内部持有 `self.segmenter = DeepLabV3Segmenter(device)`，所以要通过双层属性访问底层模型对象。

**正确调用链**：
```python
segmenter          # PortraitSegmenter 实例
segmenter.segmenter  # DeepLabV3Segmenter 实例
segmenter.segmenter.segment(image)
```

---

## 2. OpenCV 使用 BGR，不是 RGB

**现象**：`cv2.imread` 读取的是 BGR 图像。

**约定**：
- 主流程中内部处理统一 BGR
- 如需展示到网页或 notebook，需手动 `BGR -> RGB`

---

## 3. 模型输入尺寸强制 520×520

**现象**：`DeepLabV3Segmenter.preprocess()` 会先 resize 到 `(520, 520)`，推理后再恢复原尺寸。

**影响**：很小图像和超高分辨率图像都可能出现细节损失。

---

## 4. 首次运行需联网下载模型权重

**现象**：`deeplabv3_resnet50(pretrained=True)` 首次运行会下载预训练权重。

**建议**：离线环境提前缓存权重，或在可联网环境先跑一次。

---

## 5. `app.py` 仅输出透明背景图

**现状**：当前入口只保留最简功能，输出透明背景 PNG，不再支持：
- 纯色背景
- 图片背景替换
- 批量处理

如需这些能力，需要自行在 `app.py` 恢复对应参数和流程。
