# utils/visualize.py
import cv2
import matplotlib.pyplot as plt
import numpy as np

def visualize_result(image, mask, result=None, save_path=None):
    """可视化分割结果"""
    fig, axes = plt.subplots(1, 3 if result else 2, figsize=(15, 5))
    
    # 原图
    axes[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    axes[0].set_title('原图')
    axes[0].axis('off')
    
    # 掩码
    axes[1].imshow(mask, cmap='gray')
    axes[1].set_title('人像掩码')
    axes[1].axis('off')
    
    # 结果（如果有）
    if result is not None:
        if len(result.shape) == 3 and result.shape[2] == 4:
            # RGBA 图像
            axes[2].imshow(cv2.cvtColor(result, cv2.COLOR_BGRA2RGBA))
        else:
            axes[2].imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        axes[2].set_title('处理结果')
        axes[2].axis('off')
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.show()

def create_comparison_grid(images, titles, save_path=None):
    """创建对比图网格"""
    n = len(images)
    fig, axes = plt.subplots(1, n, figsize=(5*n, 5))
    
    for i, (img, title) in enumerate(zip(images, titles)):
        if len(img.shape) == 2:
            axes[i].imshow(img, cmap='gray')
        else:
            axes[i].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        axes[i].set_title(title)
        axes[i].axis('off')
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.show()