---
topic: 系统架构、模块依赖与请求处理流程
keywords: [架构, 模块依赖, 流程, 分层, Streamlit, DeepLabV3, PortraitSegmenter]
triggers: [系统怎么设计的, 模块关系, 调用流程, 整体架构]
confidence: L1
source: app.py, utils/segment.py, models/deeplabv3.py
updated: 2026-06-09
---

# 系统架构

## 分层架构

```
┌─────────────────────────────────────────┐
│              表现层 (UI)                 │
│   app.py  — Streamlit Web 应用           │
│   · 图片上传/展示                         │
│   · 参数配置（背景类型/形态学选项）         │
│   · 结果下载/批量处理                     │
└────────────────────┬────────────────────┘
                     │ 调用
┌────────────────────▼────────────────────┐
│            业务逻辑层 (Utils)             │
│   utils/segment.py — PortraitSegmenter  │
│   · 文件路径级别的分割接口                 │
│   · 封装底层模型，对外屏蔽实现细节          │
│                                         │
│   utils/visualize.py — 可视化工具        │
│   · matplotlib 绘制对比图                │
│   · 独立模块，可单独使用                  │
└────────────────────┬────────────────────┘
                     │ 调用
┌────────────────────▼────────────────────┐
│              模型层 (Models)             │
│   models/deeplabv3.py                   │
│   — DeepLabV3Segmenter                  │
│   · 加载 torchvision 预训练模型           │
│   · preprocess: BGR→RGB→Tensor→归一化   │
│   · 推理：torch.no_grad()               │
│   · postprocess: 提取 COCO 类别 15      │
└────────────────────┬────────────────────┘
                     │ 调用
┌────────────────────▼────────────────────┐
│           第三方依赖 (External)           │
│   torchvision.models.segmentation       │
│   .deeplabv3_resnet50(pretrained=True)  │
│   COCO 预训练权重（约 160MB，首次自动下载）│
└─────────────────────────────────────────┘
```

---

## 核心类/函数一览

| 模块 | 类/函数 | 职责 |
|------|---------|------|
| `models/deeplabv3.py` | `DeepLabV3Segmenter` | 模型加载、推理、前后处理 |
| `models/deeplabv3.py` | `DeepLabV3Segmenter.segment(image)` | 输入 BGR numpy 图，输出二值掩码 |
| `models/deeplabv3.py` | `DeepLabV3Segmenter.remove_background()` | 将背景像素替换为指定 BGR 颜色 |
| `models/deeplabv3.py` | `DeepLabV3Segmenter.extract_portrait()` | 输出带 Alpha 通道的 BGRA 图 |
| `utils/segment.py` | `PortraitSegmenter` | 封装层，持有 `self.segmenter` 实例 |
| `utils/segment.py` | `PortraitSegmenter.segment_image()` | 文件路径 → 掩码 + 结果图 |
| `utils/visualize.py` | `visualize_result()` | matplotlib 展示原图/掩码/结果三联图 |
| `utils/visualize.py` | `create_comparison_grid()` | N 图对比网格 |
| `app.py` | `load_segmenter()` | `@st.cache_resource` 单例加载 |

---

## 单张图片分割请求流程

```
用户上传图片
      │
      ▼
app.py: cv2.imdecode → numpy BGR image
      │
      ▼
app.py: segmenter.segmenter.segment(image)  ← 注意双层访问
      │          │
      │          ▼
      │   DeepLabV3Segmenter.segment()
      │     ├─ preprocess(): resize(520,520) → BGR→RGB → Tensor → 归一化
      │     ├─ model(input_tensor): PyTorch 推理
      │     └─ postprocess(): argmax → 取类别15 → resize回原尺寸 → 形态学
      │
      ▼
app.py: 可选形态学再处理 (MORPH_OPEN / MORPH_CLOSE)
      │
      ▼
根据背景类型分支:
  ├─ 透明背景 → extract_portrait() → BGRA PNG
  ├─ 纯色背景 → remove_background() → BGR JPG
  └─ 图片背景 → 手动 numpy 合成 → BGR JPG
```

---

## 批量处理流程

```
用户上传多张图片 → 循环调用 segment() + extract_portrait()
      │
      ▼
结果写入 batch_results/ 临时目录
      │
      ▼
打包为 batch_results.zip → 提供下载按钮
```

---

## 模型信息

| 项目 | 值 |
|------|----|
| 模型名 | DeepLabV3 with ResNet50 backbone |
| 预训练数据集 | COCO 2017 |
| 人物类别 ID | 15 |
| 输入尺寸 | 520×520（内部强制 resize） |
| 输出 | 与原图同尺寸的二值掩码（uint8, 0 or 255） |
| 模型大小 | 约 160MB（首次运行自动下载） |
| 推理设备 | CPU（默认）|
