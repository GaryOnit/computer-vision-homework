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

⚠️ **注意**：当前 `app.py` 中**未引用本模块**，这是一个独立的离线工具（见 `implicit-knowledge.md` #8）。

---

## 函数

### `visualize_result(image, mask, result=None, save_path=None)`

展示三联图：原图 | 掩码 | 处理结果（result 可选）。

| 参数 | 类型 | 说明 |
|------|------|------|
| `image` | BGR numpy | 原始图像 |
| `mask` | uint8 numpy | 二值掩码 |
| `result` | numpy \| None | 处理结果图，None 时只显示两列 |
| `save_path` | str \| None | 若指定则保存为文件 |

- 原图：BGR→RGB 转换后展示
- 掩码：灰度展示（`cmap='gray'`）
- 结果：自动检测是否为 BGRA（4通道），BGRA→RGBA 转换后展示

### `create_comparison_grid(images, titles, save_path=None)`

创建任意数量图像的横向对比网格，每列宽 5 英寸。

| 参数 | 类型 | 说明 |
|------|------|------|
| `images` | list of numpy | 图像列表，支持灰度和 BGR |
| `titles` | list of str | 各图标题，需与 images 等长 |
| `save_path` | str \| None | 若指定则保存为文件 |

灰度图（2 维）直接展示，BGR 图自动转 RGB。

---

## 使用示例（脚本中）

```python
from utils.visualize import visualize_result
from utils.segment import PortraitSegmenter

seg = PortraitSegmenter()
mask, result = seg.segment_image("photo.jpg", bg_replace='transparent')
import cv2
image = cv2.imread("photo.jpg")
visualize_result(image, mask, result, save_path="comparison.png")
```
