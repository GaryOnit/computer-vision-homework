---
topic: visualize.py — matplotlib 可视化工具函数
keywords: [visualize, 可视化, matplotlib, visualize_result, create_comparison_grid, 对比图]
triggers: [怎么可视化结果, 画对比图, visualize_result, matplotlib]
confidence: L1
source: utils/visualize.py
updated: 2026-06-09
---

# visualize.py — 可视化工具

**文件路径**：`utils/visualize.py`

## 模块职责

提供离线脚本/Jupyter 环境下的 matplotlib 可视化工具，用于查看分割结果。

⚠️ 注意：当前 `app.py` 中未引用本模块，这是一个独立的离线工具。

---

## 函数

### `visualize_result(image, mask, result=None, save_path=None)`

展示原图、掩码和结果图。

| 参数 | 类型 | 说明 |
|------|------|------|
| `image` | BGR numpy | 原始图像 |
| `mask` | uint8 numpy | 二值掩码 |
| `result` | numpy \| None | 处理结果图，None 时只显示两列 |
| `save_path` | str \| None | 若指定则保存为文件 |

- 原图：BGR->RGB 转换后展示
- 掩码：灰度展示（`cmap='gray'`）
- 结果：若为 BGRA，先转 RGBA 再展示

### `create_comparison_grid(images, titles, save_path=None)`

创建任意数量图像的横向对比网格。

| 参数 | 类型 | 说明 |
|------|------|------|
| `images` | list of numpy | 图像列表，支持灰度和 BGR |
| `titles` | list of str | 标题列表，需与 images 等长 |
| `save_path` | str \| None | 若指定则保存为文件 |

---

## 使用示例

```python
from utils.visualize import visualize_result
from utils.segment import PortraitSegmenter
import cv2

seg = PortraitSegmenter()
mask, result = seg.segment_image("photo.jpg", bg_replace='transparent')
image = cv2.imread("photo.jpg")
visualize_result(image, mask, result, save_path="comparison.png")
```
