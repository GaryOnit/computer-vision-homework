---
topic: PortraitSegmenter 类 — 高层封装，提供文件路径级别的分割接口
keywords: [PortraitSegmenter, segment, 封装, 文件路径, segment_image, segment_with_mask]
triggers: [PortraitSegmenter怎么用, 文件路径分割, 封装层]
confidence: L1
source: utils/segment.py
updated: 2026-06-09
---

# PortraitSegmenter

**文件路径**：`utils/segment.py`

## 类职责

对 `DeepLabV3Segmenter` 的高层封装，提供更便捷的接口：
- 文件路径级别的单图分割（自动读取/保存文件）
- 支持多种背景替换模式
- 对外屏蔽底层 Tensor/OpenCV 细节

---

## 构造函数

```python
PortraitSegmenter(device='cpu')
```

内部初始化 `self.segmenter = DeepLabV3Segmenter(device)`。

⚠️ **注意**：`app.py` 中通过 `segmenter.segmenter` 访问底层模型实例，而非通过本类的封装方法（见 `implicit-knowledge.md` #1）。

---

## 方法

### `segment_image(image_path, output_path=None, bg_replace=None) → (mask, result)`

从文件路径读取图像，分割后可选择保存结果。

| 参数 | 类型 | 说明 |
|------|------|------|
| `image_path` | str | 输入图像路径 |
| `output_path` | str \| None | 若指定则保存结果到此路径 |
| `bg_replace` | BGR tuple \| `'transparent'` \| None | 背景处理方式 |

`bg_replace` 取值说明：
- `None`：不替换背景，返回人像区域绿色高亮叠加图
- `'transparent'`：调用 `extract_portrait()`，返回 BGRA
- `(B,G,R)` 元组：调用 `remove_background()`，替换为纯色

返回：`(mask, result)`，读取失败时返回 `(None, None)`

### `segment_with_mask(image, mask=None) → mask`

对已有 numpy 图像做分割。若 `mask` 不为 None 则直接返回，否则调用 `self.segmenter.segment(image)`。

**使用场景**：需要传入自定义掩码时绕过模型推理。

---

## 与 app.py 的关系

`app.py` 加载 `PortraitSegmenter` 实例后，**绕过了封装方法**，直接通过 `segmenter.segmenter.segment()` 调用底层方法。这意味着 `segment_image()` 的文件路径接口在 Web UI 中**未被使用**，主要用于脚本场景。
