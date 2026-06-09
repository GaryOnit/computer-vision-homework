# utils/segment.py
import cv2
import numpy as np
import torch
from models.deeplabv3 import DeepLabV3Segmenter

class PortraitSegmenter:
    """人像分割器封装"""
    
    def __init__(self, device='cpu'):
        self.segmenter = DeepLabV3Segmenter(device)
    
    def segment_image(self, image_path, output_path=None, bg_replace=None):
        """
        分割单张图像
        Args:
            image_path: 输入图像路径
            output_path: 输出路径
            bg_replace: 替换背景颜色 (BGR) 或 'transparent'
        Returns:
            mask: 人像掩码
            result: 处理后的图像
        """
        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            print(f"无法读取图像: {image_path}")
            return None, None
        
        # 分割
        mask = self.segmenter.segment(image)
        
        # 处理结果
        if bg_replace == 'transparent':
            result = self.segmenter.extract_portrait(image, mask)
        elif bg_replace is not None:
            result = self.segmenter.remove_background(image, mask, bg_replace)
        else:
            # 生成叠加效果图
            result = image.copy()
            result[mask == 255] = [0, 255, 0]  # 人像区域绿色高亮
        
        # 保存
        if output_path:
            cv2.imwrite(output_path, result)
            print(f"结果已保存: {output_path}")
        
        return mask, result
    
    def segment_with_mask(self, image, mask=None):
        """使用已有掩码处理图像"""
        if mask is None:
            mask = self.segmenter.segment(image)
        return mask