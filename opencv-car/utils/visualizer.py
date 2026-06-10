# visualizer.py — 绘制与渲染模块
import cv2
import numpy as np
from utils.config import (
    BOX_COLOR,
    LINE_COLOR,
    TEXT_COLOR,
    FONT_SCALE,
    THICKNESS,
)


class Visualizer:
    """负责在帧上绘制边界框、Track ID、计数线、计数看板。"""

    def __init__(self, line_y: int, frame_width: int):
        self.line_y = line_y
        self.frame_width = frame_width

    def draw(self, frame: np.ndarray, tracks, count: int,
             upward_ids: set = None) -> np.ndarray:
        """
        在 frame 上叠加所有可视化元素。

        Args:
            frame      : 原始帧（BGR numpy array）
            tracks     : ultralytics Results 对象，可为 None
            count      : 当前累计过车数
            upward_ids : 需要绘制的 track_id 集合（方向向上的车辆）；
                         若为 None 则绘制所有车辆（向后兼容）

        Returns:
            叠加了标注的新帧（不修改原帧）
        """
        out = frame.copy()

        # 1. 绘制计数线
        cv2.line(
            out,
            (0, self.line_y),
            (self.frame_width, self.line_y),
            LINE_COLOR,
            THICKNESS,
        )

        # 2. 绘制车辆边界框 + Track ID
        if tracks is not None and tracks.boxes is not None:
            boxes = tracks.boxes
            xyxy = boxes.xyxy.cpu().numpy()
            ids  = boxes.id.cpu().numpy().astype(int) if boxes.id is not None else []

            for i, box in enumerate(xyxy):
                # 若指定了 upward_ids，只绘制上行车辆；否则绘制所有（向后兼容）
                if len(ids) > i:
                    tid = ids[i]
                    if upward_ids is not None and tid not in upward_ids:
                        continue
                else:
                    tid = None
                    if upward_ids is not None:
                        continue  # 无 ID 时若启用过滤则跳过

                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(out, (x1, y1), (x2, y2), BOX_COLOR, THICKNESS)

                if tid is not None:
                    label = f"ID:{tid}"
                    (tw, th), _ = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE * 0.6, 1
                    )
                    cv2.rectangle(
                        out,
                        (x1, y1 - th - 6),
                        (x1 + tw + 4, y1),
                        BOX_COLOR, -1,
                    )
                    cv2.putText(
                        out, label,
                        (x1 + 2, y1 - 4),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        FONT_SCALE * 0.6,
                        TEXT_COLOR, 1, cv2.LINE_AA,
                    )

        # 3. 绘制计数看板（左上角半透明背景）
        panel_text = f"Count: {count}"
        (pw, ph), _ = cv2.getTextSize(
            panel_text, cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, THICKNESS
        )
        overlay = out.copy()
        cv2.rectangle(overlay, (10, 10), (10 + pw + 20, 10 + ph + 20), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, out, 0.5, 0, out)
        cv2.putText(
            out, panel_text,
            (20, 10 + ph + 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            FONT_SCALE,
            TEXT_COLOR, THICKNESS, cv2.LINE_AA,
        )

        return out
