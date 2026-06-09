# app.py
import streamlit as st
import cv2
import numpy as np
import os
import zipfile

from utils.segment import PortraitSegmenter

# 页面配置
st.set_page_config(
    page_title="人像分割系统",
    page_icon="👤",
    layout="wide"
)

st.title("👤 人像分割系统")
st.markdown("上传照片，自动分割人像，一键更换背景")

# 初始化分割器
@st.cache_resource
def load_segmenter():
    with st.spinner("正在加载模型，首次运行需下载（约160MB）..."):
        return PortraitSegmenter(device='cpu')

try:
    segmenter = load_segmenter()
    st.success("✅ 模型加载成功")
except Exception as e:
    st.error(f"❌ 模型加载失败: {e}")
    st.stop()

# ==================== 侧边栏设置 ====================
st.sidebar.header("⚙️ 参数设置")

# 图片上传方式（移除粘贴图片选项）
upload_method = st.sidebar.radio(
    "图片上传方式",
    ["📁 文件上传", "📂 选择本地文件路径"]
)

# 背景设置
bg_type = st.sidebar.radio(
    "背景类型",
    ["🔲 透明背景(PNG)", "🎨 纯色背景", "🖼️ 图片背景"]
)

if bg_type == "🎨 纯色背景":
    bg_color = st.sidebar.color_picker("选择背景颜色", "#00ff00")
    bg_color_bgr = (
        int(bg_color[5:7], 16),
        int(bg_color[3:5], 16),
        int(bg_color[1:3], 16)
    )
elif bg_type == "🖼️ 图片背景":
    bg_image_file = st.sidebar.file_uploader("上传背景图片", type=['jpg', 'png', 'jpeg'])

# ==================== 图片导入 ====================
image = None
image_path = None

if upload_method == "📁 文件上传":
    uploaded_file = st.file_uploader("选择人像照片", type=['jpg', 'jpeg', 'png'])
    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        st.success("✅ 图片已加载")

elif upload_method == "📂 选择本地文件路径":
    file_path = st.text_input("请输入图片文件路径:", placeholder="例如: C:/Users/xxx/photo.jpg")
    if file_path and os.path.exists(file_path):
        image = cv2.imread(file_path)
        image_path = file_path
        st.success(f"✅ 已加载: {os.path.basename(file_path)}")
    elif file_path:
        st.error("文件不存在，请检查路径")

# ==================== 处理图片 ====================
if image is not None:
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="原图", use_column_width=True)
    
    # 处理选项
    with st.expander("🔧 高级选项"):
        col_a, col_b = st.columns(2)
        with col_a:
            morph_open = st.checkbox("形态学开运算（去除噪点）", value=True)
            morph_close = st.checkbox("形态学闭运算（填充空洞）", value=True)
    
    if st.button("🚀 开始分割", type="primary", use_container_width=True):
        with st.spinner("正在分割人像..."):
            # 获取掩码
            mask = segmenter.segmenter.segment(image)
            
            # 形态学处理
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            if morph_open:
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            if morph_close:
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # 生成结果
            if bg_type == "🔲 透明背景(PNG)":
                result = segmenter.segmenter.extract_portrait(image, mask)
                result_display = cv2.cvtColor(result, cv2.COLOR_BGRA2RGBA)
                
            elif bg_type == "🎨 纯色背景":
                result = segmenter.segmenter.remove_background(image, mask, bg_color_bgr)
                result_display = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
                
            else:  # 图片背景
                if 'bg_image_file' in locals() and bg_image_file is not None:
                    bg_bytes = np.asarray(bytearray(bg_image_file.read()), dtype=np.uint8)
                    bg_image = cv2.imdecode(bg_bytes, cv2.IMREAD_COLOR)
                    bg_image = cv2.resize(bg_image, (image.shape[1], image.shape[0]))
                    
                    result = image.copy()
                    result[mask == 0] = bg_image[mask == 0]
                    result_display = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
                else:
                    result = segmenter.segmenter.remove_background(image, mask, (0, 255, 0))
                    result_display = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
                    st.warning("未上传背景图片，使用绿色背景")
        
        with col2:
            st.image(result_display, caption="分割结果", use_column_width=True)
        
        # 下载按钮
        st.markdown("---")
        col_d1, col_d2, col_d3 = st.columns(3)
        
        with col_d1:
            if bg_type == "🔲 透明背景(PNG)":
                temp_path = "temp_result.png"
                cv2.imwrite(temp_path, result)
                with open(temp_path, "rb") as f:
                    st.download_button(
                        label="📥 下载 PNG (透明背景)",
                        data=f,
                        file_name="portrait_transparent.png",
                        mime="image/png"
                    )
                os.remove(temp_path)
            else:
                temp_path = "temp_result.jpg"
                cv2.imwrite(temp_path, result)
                with open(temp_path, "rb") as f:
                    st.download_button(
                        label="📥 下载 JPG",
                        data=f,
                        file_name="portrait_result.jpg",
                        mime="image/jpeg"
                    )
                os.remove(temp_path)
        
        with col_d2:
            temp_mask_path = "temp_mask.png"
            cv2.imwrite(temp_mask_path, mask)
            with open(temp_mask_path, "rb") as f:
                st.download_button(
                    label="🎭 下载掩码",
                    data=f,
                    file_name="portrait_mask.png",
                    mime="image/png"
                )
            os.remove(temp_mask_path)
        
        with col_d3:
            portrait_pixels = (mask == 255).sum()
            total_pixels = mask.size
            ratio = portrait_pixels / total_pixels * 100
            st.metric("人像占比", f"{ratio:.1f}%")

# ==================== 批量处理 ====================
st.markdown("---")
st.subheader("📁 批量处理多张图片")

uploaded_files = st.file_uploader(
    "选择多张照片",
    type=['jpg', 'jpeg', 'png'],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("开始批量处理", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        temp_dir = "batch_results"
        os.makedirs(temp_dir, exist_ok=True)
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"处理中: {uploaded_file.name} ({i+1}/{len(uploaded_files)})")
            
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            
            mask = segmenter.segmenter.segment(img)
            result = segmenter.segmenter.extract_portrait(img, mask)
            
            output_path = os.path.join(temp_dir, f"result_{i}_{uploaded_file.name}")
            cv2.imwrite(output_path, result)
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        status_text.text("批量处理完成！")
        st.success(f"✅ 处理完成！结果保存在 {temp_dir} 目录")
        
        zip_path = "batch_results.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for f in os.listdir(temp_dir):
                zipf.write(os.path.join(temp_dir, f), f)
        
        with open(zip_path, "rb") as f:
            st.download_button(
                label="📦 下载所有结果 (ZIP)",
                data=f,
                file_name="portrait_results.zip",
                mime="application/zip"
            )

# ==================== 使用说明 ====================
with st.sidebar.expander("📖 使用说明", expanded=True):
    st.markdown("""
    ### 上传图片方式
    1. **文件上传**：直接点击上传
    2. **本地路径**：输入完整文件路径
    
    ### 背景选项
    - **透明背景**：保存为 PNG 格式
    - **纯色背景**：自定义任意颜色
    - **图片背景**：上传背景图合成
    
    ### 高级选项
    - 形态学开运算：去除小噪点
    - 形态学闭运算：填充小空洞
    
    ### 批量处理
    支持同时处理多张图片，结果打包下载
    """)

st.sidebar.markdown("---")
st.sidebar.caption(f"模型: DeepLabV3 (COCO预训练)")
st.sidebar.caption("© 人像分割系统")