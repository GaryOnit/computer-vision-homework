---
topic: DeepLabV3Segmenter 类 — 模型加载、推理与前后处理
keywords: [DeepLabV3, DeepLabV3Segmenter, 语义分割, 模型, 推理, 预处理, 后处理, COCO, ResNet50]
triggers: [模型怎么加载, 推理流程, preprocess, postprocess, segment, remove_background, extract_portrait]
confidence: L1
source: models/deeplabv3.py
updated: 2026-06-09
---

# DeepLabV3Segmenter

**文件路径**：`models/deeplabv3.py`

## 类职责

封装 `torchvision` 提供的 DeepLabV3-ResNet50 语义分割模型，对外提供：
1. 模型加载与设备管理
2. 图像预处理（BGR numpy → 归一化 Tensor）
3. 模型推理
4. 后处理（提取人像掩码）
5. 背景替换与透明抠图

---

## 构造函数

```python
DeepLabV3Segmenter(device='cpu')
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `device` | str | `'cpu'` | PyTorch 设备，支持 `'cpu'` / `'cuda'` |

构造时自动调用 `load_model()`，同步加载预训练权重。

---

## 方法

### `load_model()`

加载 `deeplabv3_resnet50(pretrained=True)`，设置为 eval 模式，移至指定 device。首次调用需联网下载约 160MB。

### `preprocess(image) → Tensor`

| 步骤 | 操作 |
|------|------|
| 1 | `cv2.resize(image, (520, 520))` — 强制 resize |
| 2 | `cv2.cvtColor(BGR→RGB)` |
| 3 | 除以 255.0，转 float32 |
| 4 | `transforms.ToTensor()` |
| 5 | `transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])` |
| 6 | `.unsqueeze(0)` — 增加 batch 维 |

返回形状：`[1, 3, 520, 520]`

### `postprocess(output, original_size) → numpy uint8`

1. 取 `output['out']`（模型输出字典中的主分割头）
2. `torch.argmax(dim=1)` → 每像素预测类别
3. 提取类别 15（COCO 中的 "person"），生成 `uint8` 掩码（255=人，0=背景）
4. `cv2.resize` 回原始尺寸，插值方法 `INTER_NEAREST`
5. 形态学处理：`MORPH_CLOSE` → `MORPH_OPEN`（5×5 椭圆核）

⚠️ **注意**：内置形态学处理与 `app.py` 中的可选形态学**会叠加执行两次**（见 `implicit-knowledge.md` #5）。

### `segment(image) → mask`

完整推理流程：`preprocess` → `model` → `postprocess`。使用 `torch.no_grad()` 禁用梯度。

```python
mask = segmenter.segment(image)  # image: BGR numpy, mask: uint8 numpy (255/0)
```

### `remove_background(image, mask, bg_color=(0,255,0)) → BGR numpy`

将 `mask==0` 的背景区域替换为 `bg_color`（BGR 格式）。硬切换，无羽化。

### `extract_portrait(image, mask) → BGRA numpy`

将图像转为 4 通道 BGRA，以 `mask` 作为 Alpha 通道（255=不透明，0=完全透明），返回透明背景图。
