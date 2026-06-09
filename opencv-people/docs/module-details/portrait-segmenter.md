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

对 `DeepLabV3Segmenter` 的高层封装，提供更便捷接口：
- 文件路径级别的单图分割（自动读取/保存文件）
- 支持透明背景和纯色背景两类输出
- 对外屏蔽底层 Tensor/OpenCV 细节

---

## 构造函数

```python
PortraitSegmenter(device='cpu')
```

内部初始化 `self.segmenter = DeepLabV3Segmenter(device)`。

⚠️ 注意：`app.py` 里通过 `segmenter.segmenter` 访问底层模型实例，而不是只使用本类封装方法。

---

## 方法

### `segment_image(image_path, output_path=None, bg_replace=None) -> (mask, result)`

从文件路径读取图像，分割后可选择保存结果。

| 参数 | 类型 | 说明 |
|------|------|------|
| `image_path` | str | 输入图像路径 |
| `output_path` | str \| None | 若指定则保存结果到此路径 |
| `bg_replace` | BGR tuple \| `'transparent'` \| None | 背景处理方式 |

`bg_replace` 取值说明：
- `None`：返回人像绿色高亮叠加图
- `'transparent'`：调用 `extract_portrait()`，返回 BGRA
- `(B,G,R)`：调用 `remove_background()`，替换纯色背景

返回值：`(mask, result)`；读取失败时返回 `(None, None)`。

### `segment_with_mask(image, mask=None) -> mask`

对已有 numpy 图像做分割。若 `mask` 不为 None 则直接返回，否则调用 `self.segmenter.segment(image)`。

---

## 与 app.py 的关系

当前最简 `app.py` 主流程直接调用：
- `segmenter.segmenter.segment(image)`
- `segmenter.segmenter.extract_portrait(image, mask)`

因此 `segment_image()` 目前更适合在脚本或二次开发场景中复用。
