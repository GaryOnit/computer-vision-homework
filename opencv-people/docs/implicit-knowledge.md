---
topic: 已知坑、反直觉设计与特殊约定
keywords: [踩坑, 注意事项, 坑, 特殊设计, 反直觉, 已知问题, BGR, 双层访问]
triggers: [有什么坑, 注意什么, 为什么这样写, 反直觉行为, 特殊约定]
confidence: L1
source: app.py, models/deeplabv3.py, utils/segment.py
updated: 2026-06-09
---

# 已知坑与特殊设计

## 1. 双层 `.segmenter` 访问（高频踩坑）

**现象**：`app.py` 中访问模型的方式是 `segmenter.segmenter.segment(image)`，看起来像 typo 但实际正确。

**原因**：`load_segmenter()` 返回的是 `PortraitSegmenter` 实例（变量名 `segmenter`），而 `PortraitSegmenter` 内部持有 `self.segmenter = DeepLabV3Segmenter(device)` 属性，因此需要双层访问。

**正确调用链**：
```python
segmenter          # PortraitSegmenter 实例
segmenter.segmenter  # DeepLabV3Segmenter 实例
segmenter.segmenter.segment(image)  # 实际推理方法
```

---

## 2. OpenCV 使用 BGR，不是 RGB

**现象**：直接用 `cv2.imread` 读取的图像是 BGR 格式，若不转换就传给 Streamlit 显示，颜色会偏色（红蓝通道互换）。

**约定**：
- 内部处理全程用 BGR（OpenCV 原生）
- 传给 `st.image()` 前必须转为 RGB：`cv2.cvtColor(image, cv2.COLOR_BGR2RGB)`
- 透明背景图用 BGRA，展示前转 RGBA：`cv2.cvtColor(result, cv2.COLOR_BGRA2RGBA)`

---

## 3. 颜色选择器返回 HEX，需手动转 BGR

**现象**：`st.sidebar.color_picker()` 返回格式为 `"#RRGGBB"` 的十六进制字符串，但 OpenCV 需要 BGR 元组。

**代码中的转换逻辑**（`app.py` 第 50-54 行）：
```python
bg_color_bgr = (
    int(bg_color[5:7], 16),   # B
    int(bg_color[3:5], 16),   # G
    int(bg_color[1:3], 16)    # R
)
```
注意字符串切片顺序是反的（R在前G在中B在后），转换时要对调位置。

---

## 4. 模型输入尺寸强制 520×520

**现象**：DeepLabV3 `preprocess()` 无论输入图像多大，都会先 resize 到 `(520, 520)`，推理后再用 `INTER_NEAREST` 恢复原始尺寸。

**影响**：对于非常小的图像（如 50×50），resize 到 520 会引入插值误差；对于超高分辨率图（4K+），推理精度可能不足。

---

## 5. 模型在 postprocess 内已做一次形态学处理，app.py 还会再做一次

**现象**：`DeepLabV3Segmenter.postprocess()` 内部已执行 `MORPH_CLOSE + MORPH_OPEN`，但 `app.py` 里用户勾选后还会对返回的 mask **再做一次** `MORPH_OPEN + MORPH_CLOSE`（顺序还不同）。

**结果**：形态学实际被执行了两次，用户勾选高级选项时相当于做了双重形态学处理。如需精确控制，应在 `postprocess()` 中去掉内置的形态学处理，只保留 `app.py` 的可选处理。

---

## 6. 批量处理结果目录不自动清理

**现象**：批量处理完成后，`batch_results/` 目录和 `batch_results.zip` 文件**不会自动删除**，会持续占用磁盘空间。

**当前状态**：代码未实现清理逻辑，需用户手动删除。

---

## 7. 图片背景合成使用 numpy 索引，非 alpha 混合

**现象**：图片背景替换逻辑（`app.py` 第 119-121 行）是：
```python
result = image.copy()
result[mask == 0] = bg_image[mask == 0]
```
这是**硬切换**（mask 边缘是 0 或 255 的二值边界），没有边缘羽化/alpha 混合，背景替换后人像边缘可能有锯齿。

---

## 8. `utils/visualize.py` 当前未被 app.py 引用

**现象**：`visualize.py` 提供 matplotlib 可视化功能，但 `app.py` 中**没有 import 也没有调用**，是一个独立的离线工具。

**用途**：仅在脚本/Jupyter 中直接调用，不属于 Web UI 流程的一部分。

---

## 9. 首次运行需联网下载约 160MB 模型权重

**现象**：`segmentation.deeplabv3_resnet50(pretrained=True)` 会从 PyTorch Hub 自动下载 COCO 预训练权重。

**离线环境**：需提前下载权重文件并手动指定路径，或使用 `weights_only=True` 加载本地文件。
