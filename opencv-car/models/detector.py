# detector.py — YOLOv8 检测模块（用于单帧调试）
import torch
from ultralytics import YOLO
from utils.config import MODEL_PATH, CONF_THRESHOLD, IOU_THRESHOLD, VEHICLE_CLASSES


def get_device() -> str:
    """选择推理设备：优先 MPS（Apple Silicon），回退 CPU。"""
    if torch.backends.mps.is_available():
        try:
            _ = torch.zeros(1).to("mps")
            return "mps"
        except RuntimeError:
            pass
    return "cpu"


class Detector:
    """封装 YOLOv8 目标检测，仅返回车辆类别检测结果。"""

    def __init__(self):
        self.device = get_device()
        print(f"[Detector] 使用设备: {self.device}")
        self.model = YOLO(MODEL_PATH)

    def detect(self, frame):
        """
        对单帧执行检测。

        Args:
            frame: BGR numpy array（OpenCV 帧）

        Returns:
            ultralytics Results 对象（供直接消费）
        """
        results = self.model.predict(
            source=frame,
            conf=CONF_THRESHOLD,
            iou=IOU_THRESHOLD,
            classes=VEHICLE_CLASSES,
            device=self.device,
            verbose=False,
        )
        return results[0]
