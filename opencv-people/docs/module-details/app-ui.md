---
topic: app.py — 命令行入口逻辑
keywords: [app.py, CLI, 命令行, 参数解析, 输入输出, main, build_parser]
triggers: [app.py做了什么, 怎么运行, 命令行入口, 参数含义]
confidence: L1
source: app.py
updated: 2026-06-09
---

# app.py — CLI 入口层

**文件路径**：`app.py`

## 功能职责

`app.py` 只负责最小闭环：

1. 解析命令行参数（输入图 + 可选输出图）
2. 读取输入图像
3. 调用分割模型并提取透明背景人像
4. 保存结果文件并打印输出路径

---

## 命令行参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `input` | 是 | 输入图片路径 |
| `-o, --output` | 否 | 输出图片路径；默认 `<input_stem>_portrait.png` |

---

## 主流程

```python
args = build_parser().parse_args()
input_path = Path(args.input).expanduser().resolve()
image = cv2.imread(str(input_path), cv2.IMREAD_COLOR)

segmenter = PortraitSegmenter(device="cpu")
mask = segmenter.segmenter.segment(image)
result = segmenter.segmenter.extract_portrait(image, mask)

cv2.imwrite(str(output_path), result)
```

---

## 注意事项

- 输出固定为透明背景 PNG（BGRA）
- 默认 CPU 推理
- 首次运行会触发模型权重下载
- `PortraitSegmenter` 只是封装层，入口直接调用了底层 `segmenter.segmenter` 方法
