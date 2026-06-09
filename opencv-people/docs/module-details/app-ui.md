---
topic: app.py — Streamlit Web UI 层逻辑
keywords: [app.py, Streamlit, UI, 页面, 侧边栏, 文件上传, 背景替换, 批量处理, 下载, load_segmenter]
triggers: [UI怎么实现的, app.py做了什么, 页面逻辑, Streamlit页面结构]
confidence: L1
source: app.py
updated: 2026-06-09
---

# app.py — UI 层

**文件路径**：`app.py`

## 页面结构

```
页面
├── 标题：👤 人像分割系统
├── 模型加载状态提示
├── 侧边栏
│   ├── ⚙️ 参数设置
│   │   ├── 图片上传方式（文件上传 / 本地路径）
│   │   └── 背景类型（透明/纯色/图片）
│   └── 📖 使用说明（可展开）
├── 主区域（图片上传后显示）
│   ├── 原图（左列）
│   ├── 分割结果（右列，点击分割后显示）
│   ├── 🔧 高级选项（可展开）
│   │   ├── 形态学开运算 checkbox
│   │   └── 形态学闭运算 checkbox
│   ├── 🚀 开始分割 按钮
│   └── 下载区（分割后）
│       ├── 下载结果图（PNG/JPG）
│       ├── 下载掩码
│       └── 人像占比指标
└── 批量处理区
    ├── 多文件上传
    ├── 开始批量处理 按钮
    └── 下载 ZIP 按钮
```

---

## 关键实现细节

### 模型单例加载

```python
@st.cache_resource
def load_segmenter():
    return PortraitSegmenter(device='cpu')
```

`@st.cache_resource` 确保整个 Streamlit 会话中模型只加载一次，页面刷新不会重新加载。

### 图片输入两种方式

| 方式 | 实现 | 返回 |
|------|------|------|
| 文件上传 | `st.file_uploader` + `cv2.imdecode` | BGR numpy |
| 本地路径 | `st.text_input` + `cv2.imread` | BGR numpy |

### 颜色选择器的 HEX→BGR 转换

`st.color_picker()` 返回 `"#RRGGBB"`，需手动解析为 BGR 元组（见 `implicit-knowledge.md` #3）。

### 下载文件的实现方式

**先写临时文件，再读取，再删除**：
```python
cv2.imwrite("temp_result.png", result)
with open("temp_result.png", "rb") as f:
    st.download_button(..., data=f)
os.remove("temp_result.png")
```

⚠️ 临时文件写在**运行时当前目录**（即启动 `streamlit run` 的目录），不是固定路径。

### 人像占比计算

```python
portrait_pixels = (mask == 255).sum()
ratio = portrait_pixels / mask.size * 100
```

`mask.size` 是 numpy 数组总元素数（宽×高），结果为百分比。

---

## 批量处理细节

- 输出目录：`batch_results/`（相对于运行目录，自动创建）
- 输出文件名格式：`result_{序号}_{原文件名}`
- 统一使用透明背景（`extract_portrait`）输出 PNG
- ZIP 文件路径：`batch_results.zip`（不自动删除，见 `implicit-knowledge.md` #6）
