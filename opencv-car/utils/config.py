# config.py — 全局配置项
import os

# ── 路径配置 ──────────────────────────────────────────
# utils/ 目录的上一级即项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_VIDEO  = os.path.join(BASE_DIR, "vehicle.mp4")
OUTPUT_DIR   = os.path.join(BASE_DIR, "output_videos")
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, "output_counted.mp4")
MODEL_PATH   = "yolov8n.pt"          # 首次运行自动下载

# ── 检测配置 ──────────────────────────────────────────
CONF_THRESHOLD  = 0.3                # 置信度阈值
IOU_THRESHOLD   = 0.5                # NMS IoU 阈值
VEHICLE_CLASSES = [2, 5, 7]          # COCO: car=2, bus=5, truck=7

# ── 追踪配置 ──────────────────────────────────────────
TRACKER = "bytetrack.yaml"           # YOLOv8 内置追踪器配置

# ── 计数线配置（归一化坐标，相对帧高）────────────────
# 水平计数线，y 轴位置（0.0 顶部 ~ 1.0 底部），推荐 0.55 居中偏下
COUNTING_LINE_Y_RATIO = 0.55
# 防抖冷却帧数（同一辆车触发计数后，N 帧内不再重复计数）
COOLDOWN_FRAMES = 30

# ── 可视化配置 ────────────────────────────────────────
SHOW_PREVIEW = True                  # False = 无头模式（CI/无显示器环境）
BOX_COLOR    = (0, 255, 0)           # 边界框颜色（BGR 绿色）
LINE_COLOR   = (0, 0, 255)           # 计数线颜色（BGR 红色）
TEXT_COLOR   = (255, 255, 255)       # 文字颜色（BGR 白色）
FONT_SCALE   = 1.0
THICKNESS    = 2
