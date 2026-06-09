import argparse
from pathlib import Path

import cv2

from utils.segment import PortraitSegmenter


def build_parser():
    parser = argparse.ArgumentParser(description="Simple portrait segmentation")
    parser.add_argument("input", help="Input image path")
    parser.add_argument(
        "-o",
        "--output",
        help="Output image path (default: <input_name>_portrait.png)",
    )
    return parser


def main():
    args = build_parser().parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else input_path.with_name(f"{input_path.stem}_portrait.png")
    )

    image = cv2.imread(str(input_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Failed to read image: {input_path}")

    segmenter = PortraitSegmenter(device="cpu")
    mask = segmenter.segmenter.segment(image)
    result = segmenter.segmenter.extract_portrait(image, mask)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output_path), result):
        raise RuntimeError(f"Failed to save result image: {output_path}")

    print(f"Done: {output_path}")


if __name__ == "__main__":
    main()
