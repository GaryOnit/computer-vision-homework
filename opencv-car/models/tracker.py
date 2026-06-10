# tracker.py — 多目标追踪模块（基于 YOLOv8 内置 ByteTrack）
import torch
from ultralytics import YOLO
from utils.config import (
    MODEL_PATH,
    CONF_THRESHOLD,
    IOU_THRESHOLD,
    VEHICLE_CLASSES,
    TRACKER,
)


def get_device() -> str:
    """选择推理设备：优先 MPS（Apple Silicon），回退 CPU。"""
    if torch.backends.mps.is_available():
        try:
            _ = torch.zeros(1).to("mps")
            return "mps"
        except RuntimeError:
            pass
    return "cpu"


class Tracker:
    """
    封装 YOLOv8 + ByteTrack 多目标追踪。
    每帧调用 update()，返回带 track_id 的检测结果。
    """

    def __init__(self):
        self.device = get_device()
        print(f"[Tracker] 使用设备: {self.device}")
        self.model = YOLO(MODEL_PATH)

    def update(self, frame):
        """
        对单帧执行检测 + 追踪。

        Args:
            frame: BGR numpy array（OpenCV 帧）

        Returns:
            ultralytics Results 对象，boxes 含 track_id；
            若无结果返回 None。
        """
        results = self.model.track(
            source=frame,
            conf=CONF_THRESHOLD,
            iou=IOU_THRESHOLD,
            classes=VEHICLE_CLASSES,
            tracker=TRACKER,
            device=self.device,
            persist=True,    # 跨帧持久化追踪状态（关键！）
            verbose=False,
        )
        return results[0] if results else None
