# counter.py — 虚拟计数线逻辑
from utils.config import COOLDOWN_FRAMES


class LineCounter:
    """
    单方向虚拟计数线计数器。

    穿越方向：上行驶向镜头时车辆 y 坐标减小（从画面下方向上方移动），
    即 cy <= line_y < prev_cy 时触发计数。
    """

    def __init__(self, line_y: int):
        """
        Args:
            line_y: 计数线的绝对像素 y 坐标
        """
        self.line_y = line_y
        self.count = 0
        self._prev_y: dict[int, float] = {}    # track_id -> 上一帧中心点 y
        self._cooldown: dict[int, int] = {}    # track_id -> 冷却剩余帧数
        self.upward_ids: set[int] = set()      # 当前帧中方向向上（y 减小）的 track_id

    def update(self, tracks) -> int:
        """
        传入当前帧的追踪结果，更新计数。

        同时更新 self.upward_ids：包含当前帧中 y 坐标比上一帧小（即向上行驶）的
        所有 track_id，供外部（visualizer）过滤绘制使用。

        Args:
            tracks: ultralytics Results 对象（含 boxes + id），可为 None

        Returns:
            当前累计计数
        """
        # 每帧开头清空，避免上一帧残留
        self.upward_ids = set()

        if tracks is None or tracks.boxes is None:
            return self.count

        boxes = tracks.boxes
        if boxes.id is None:
            return self.count

        ids  = boxes.id.cpu().numpy().astype(int)
        xyxy = boxes.xyxy.cpu().numpy()

        # 递减所有冷却计数
        for tid in list(self._cooldown.keys()):
            self._cooldown[tid] -= 1
            if self._cooldown[tid] <= 0:
                del self._cooldown[tid]

        for tid, box in zip(ids, xyxy):
            cy = (box[1] + box[3]) / 2.0   # 当前帧中心点 y

            if tid in self._prev_y:
                prev_cy = self._prev_y[tid]
                # 方向向上：当前帧 y < 上一帧 y（车辆从画面下方向上方移动）
                if cy < prev_cy:
                    self.upward_ids.add(tid)
                # 穿越检测：上行 = y 减小方向穿越计数线
                if cy <= self.line_y < prev_cy and tid not in self._cooldown:
                    self.count += 1
                    self._cooldown[tid] = COOLDOWN_FRAMES
            # 第一次出现的 tid 不记入 upward_ids，先记录位置，下一帧再判断

            self._prev_y[tid] = cy

        return self.count

    def reset(self):
        """重置计数器状态。"""
        self.count = 0
        self._prev_y.clear()
        self._cooldown.clear()
        self.upward_ids = set()
