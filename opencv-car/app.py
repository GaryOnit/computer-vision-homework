# app.py — 公路车流量智能检测与计数系统主入口
"""
使用方法：
    python app.py                             # 正常运行（显示预览窗口）
    python app.py --no-preview                # 无头模式（不显示窗口）
    python app.py --input path/to/video.mp4   # 自定义输入视频
    python app.py --output path/to/out.mp4    # 自定义输出路径
"""
import argparse
import os
import sys

import cv2

from models.tracker import Tracker
from utils import config
from utils.counter import LineCounter
from utils.visualizer import Visualizer


def get_video_writer(
    cap: cv2.VideoCapture, output_path: str
) -> tuple[cv2.VideoWriter, str]:
    """
    尝试三种编解码器（avc1 → mp4v → MJPG），返回第一个成功的 VideoWriter。

    Returns:
        (writer, actual_output_path)
    """
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS) or 25.0

    codecs = [
        ("avc1", output_path),
        ("mp4v", output_path),
        ("MJPG", output_path.replace(".mp4", ".avi")),
    ]

    for fourcc_str, out_path in codecs:
        fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
        writer = cv2.VideoWriter(out_path, fourcc, fps, (width, height))
        if writer.isOpened():
            print(f"[Writer] 编解码器: {fourcc_str}  输出: {out_path}")
            return writer, out_path

    raise RuntimeError("无法初始化 VideoWriter，所有编解码器均失败。")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="公路车流量智能检测与计数系统")
    parser.add_argument(
        "--input", default=config.INPUT_VIDEO, help="输入视频路径"
    )
    parser.add_argument(
        "--output", default=config.OUTPUT_VIDEO, help="输出视频路径"
    )
    parser.add_argument(
        "--no-preview", action="store_true", help="禁用 OpenCV 预览窗口"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    show_preview = config.SHOW_PREVIEW and not args.no_preview

    # ── 打开输入视频 ──────────────────────────────────
    cap = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        print(f"[错误] 无法打开视频: {args.input}", file=sys.stderr)
        sys.exit(1)

    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps    = cap.get(cv2.CAP_PROP_FPS)
    print(f"[视频] {width}×{height} @ {fps:.1f}fps，共 {total} 帧")

    # ── 计算计数线绝对坐标 ────────────────────────────
    line_y = int(height * config.COUNTING_LINE_Y_RATIO)
    print(f"[计数线] y = {line_y}px（帧高 {config.COUNTING_LINE_Y_RATIO * 100:.0f}%）")

    # ── 确保输出目录存在 ──────────────────────────────
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    # ── 初始化各模块 ──────────────────────────────────
    tracker    = Tracker()
    counter    = LineCounter(line_y=line_y)
    visualizer = Visualizer(line_y=line_y, frame_width=width)
    writer, actual_output = get_video_writer(cap, args.output)

    # ── 主循环 ────────────────────────────────────────
    frame_idx = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_idx += 1
            if frame_idx % 50 == 0:
                print(f"[进度] {frame_idx}/{total} 帧  当前计数: {counter.count}")

            # 1. 追踪（内含检测）
            tracks = tracker.update(frame)

            # 2. 更新计数（同时更新 counter.upward_ids）
            count = counter.update(tracks)

            # 3. 可视化叠加（只绘制上行车辆）
            vis_frame = visualizer.draw(frame, tracks, count, upward_ids=counter.upward_ids)

            # 4. 写入输出视频（每帧写两次实现 0.5x 慢放，兼容所有播放器）
            writer.write(vis_frame)
            writer.write(vis_frame)

            # 5. 实时预览（可选）
            if show_preview:
                cv2.imshow("Vehicle Counter", vis_frame)
                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), 27):   # q 或 ESC 退出
                    print("[用户] 手动退出预览")
                    break

    except KeyboardInterrupt:
        print("\n[中断] Ctrl+C，正在保存已处理帧...")
    finally:
        cap.release()
        writer.release()
        if show_preview:
            cv2.destroyAllWindows()

    print(f"\n✅ 处理完成！")
    print(f"   共处理帧数 : {frame_idx}")
    print(f"   累计过车数 : {counter.count}")
    print(f"   输出视频   : {actual_output}")


if __name__ == "__main__":
    main()
