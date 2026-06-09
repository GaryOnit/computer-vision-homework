---
topic: 业务场景到代码路径速查表
keywords: [速查, 快速定位, 场景, 分割, 背景替换, 批量处理, 掩码, 透明背景]
triggers: [怎么实现XX, 哪个文件负责XX, 找XX功能的代码]
confidence: L1
source: app.py, utils/segment.py, models/deeplabv3.py
updated: 2026-06-09
---

# 业务场景速查表

## 场景 → 代码路径

| 我想做... | 找哪个文件 | 找哪个类/函数 |
|-----------|-----------|--------------|
| 分割人像，获取掩码 | `models/deeplabv3.py` | `DeepLabV3Segmenter.segment(image)` |
| 替换为纯色背景 | `models/deeplabv3.py` | `DeepLabV3Segmenter.remove_background(image, mask, bg_color)` |
| 提取透明背景 PNG | `models/deeplabv3.py` | `DeepLabV3Segmenter.extract_portrait(image, mask)` |
| 从文件路径分割单张图 | `utils/segment.py` | `PortraitSegmenter.segment_image(image_path, output_path, bg_replace)` |
| 对已有 numpy 图像做分割 | `utils/segment.py` | `PortraitSegmenter.segment_with_mask(image)` |
| 可视化原图+掩码+结果对比 | `utils/visualize.py` | `visualize_result(image, mask, result, save_path)` |
| 多图对比网格图 | `utils/visualize.py` | `create_comparison_grid(images, titles, save_path)` |
| Web UI 入口 | `app.py` | `load_segmenter()` + Streamlit 主流程 |
| 批量处理多张图片 | `app.py` | 第 186-221 行批量处理逻辑 |
| 图像预处理（缩放/归一化/Tensor化） | `models/deeplabv3.py` | `DeepLabV3Segmenter.preprocess(image)` |
| 模型推理后处理（提取掩码） | `models/deeplabv3.py` | `DeepLabV3Segmenter.postprocess(output, original_size)` |

---

## 术语表

| 术语 | 含义 |
|------|------|
| mask / 掩码 | 二值图像（uint8），255=人像区域，0=背景区域 |
| DeepLabV3 | 语义分割模型，基于 ResNet50，COCO 预训练 |
| COCO 类别 15 | COCO 数据集中"人"对应的类别 ID |
| BGR | OpenCV 默认的图像通道顺序（Blue-Green-Red），非 RGB |
| BGRA | BGR + Alpha 通道，用于透明背景图像 |
| PortraitSegmenter | 对 DeepLabV3Segmenter 的上层封装，提供文件路径级别的接口 |
| `@st.cache_resource` | Streamlit 缓存装饰器，确保模型只加载一次 |
| 形态学开运算 | MORPH_OPEN：先腐蚀后膨胀，用于去除掩码中的小噪点 |
| 形态学闭运算 | MORPH_CLOSE：先膨胀后腐蚀，用于填充掩码中的小空洞 |
| batch_results/ | 批量处理时临时输出目录，运行期间由代码自动创建 |

---

## 依赖关系速查

```
app.py
  └── utils/segment.py (PortraitSegmenter)
        └── models/deeplabv3.py (DeepLabV3Segmenter)
              └── torchvision.models.segmentation.deeplabv3_resnet50

utils/visualize.py  ← 独立工具，app.py 当前未直接引用
```
