# models/deeplabv3.py
import torch
import torch.nn as nn
import torchvision.models.segmentation as segmentation

class DeepLabV3Segmenter:
    """DeepLabV3 人像分割器"""
    
    def __init__(self, device='cpu'):
        self.device = device
        self.model = None
        self.load_model()
    
    def load_model(self):
        """加载预训练的 DeepLabV3 模型"""
        print("加载 DeepLabV3 模型...")
        # 使用预训练模型（在 COCO 上训练）
        self.model = segmentation.deeplabv3_resnet50(pretrained=True)
        self.model.eval()
        self.model.to(self.device)
        print("模型加载完成！")
    
    def preprocess(self, image):
        """预处理图像"""
        import cv2
        import numpy as np
        from torchvision import transforms
        
        # 调整尺寸
        image = cv2.resize(image, (520, 520))
        # 转换为 RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # 归一化
        image = image.astype(np.float32) / 255.0
        # 转换为 tensor
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])
        image_tensor = transform(image).unsqueeze(0)
        return image_tensor
    
    def postprocess(self, output, original_size):
        """后处理，提取人像掩码"""
        import cv2
        import numpy as np
        
        # 获取分割结果
        output = output['out']
        pred = torch.argmax(output, dim=1).squeeze().cpu().numpy()
        
        # COCO 数据集中，人物类别是 15
        # 其他类别可参考：0=背景, 15=人
        person_mask = (pred == 15).astype(np.uint8) * 255
        
        # 恢复原始尺寸
        person_mask = cv2.resize(person_mask, original_size, interpolation=cv2.INTER_NEAREST)
        
        # 形态学处理，去除小噪点
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        person_mask = cv2.morphologyEx(person_mask, cv2.MORPH_CLOSE, kernel)
        person_mask = cv2.morphologyEx(person_mask, cv2.MORPH_OPEN, kernel)
        
        return person_mask
    
    def segment(self, image):
        """分割人像"""
        import cv2
        
        original_size = (image.shape[1], image.shape[0])
        input_tensor = self.preprocess(image)
        input_tensor = input_tensor.to(self.device)
        
        with torch.no_grad():
            output = self.model(input_tensor)
        
        mask = self.postprocess(output, original_size)
        return mask
    
    def remove_background(self, image, mask, bg_color=(0, 255, 0)):
        """去除背景，替换为指定颜色"""
        import cv2
        import numpy as np
        
        result = image.copy()
        # 将背景区域替换为指定颜色
        result[mask == 0] = bg_color
        return result
    
    def extract_portrait(self, image, mask):
        """提取人像（透明背景）"""
        import cv2
        import numpy as np
        
        # 转换为 RGBA
        if image.shape[2] == 3:
            result = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        else:
            result = image.copy()
        
        # 设置 alpha 通道
        result[:, :, 3] = mask
        
        return result