#!/usr/bin/env python3
"""Validate bundled targets, preset permutations, and rendered preview files."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TARGET_SHA256 = "7e66af0630b5781a4606f98f4800431257eac10d235448d295798c6812f449cc"
PRESET_NAMES = ("wisetree", "blackhole", "cat", "cat2", "colorful")
PIXEL_COUNT = 128 * 128


def rgb(path: Path) -> Image.Image:
    with Image.open(path) as image:
        return image.convert("RGB")


def color_error(left: bytes, right: bytes) -> int:
    return sum((a - b) ** 2 for a, b in zip(left, right))


def main() -> None:
    target_path = ROOT / "src" / "app" / "calculate" / "target.webp"
    digest = hashlib.sha256(target_path.read_bytes()).hexdigest()
    assert digest == EXPECTED_TARGET_SHA256, digest

    legacy_target = rgb(ROOT / "src" / "app" / "calculate" / "target128.png")
    assert legacy_target.size == (128, 128)
    for size in (128, 256):
        weights = rgb(ROOT / "src" / "app" / "calculate" / f"weights{size}.png")
        assert weights.size == (size, size)
        assert weights.getextrema() == ((255, 255), (255, 255), (255, 255))

    expected_indices = list(range(PIXEL_COUNT))
    runtime_target = None
    for preset_name in PRESET_NAMES:
        preset_dir = ROOT / "presets" / preset_name
        source = rgb(preset_dir / "source.png")
        output = rgb(preset_dir / "output.png")
        preset_target = rgb(preset_dir / "target.png")
        assignments = json.loads((preset_dir / "assignments.json").read_text())

        assert source.size == output.size == preset_target.size == (128, 128)
        assert len(assignments) == PIXEL_COUNT
        assert sorted(assignments) == expected_indices
        if runtime_target is None:
            runtime_target = preset_target
        else:
            assert ImageChops.difference(runtime_target, preset_target).getbbox() is None

        source_pixels = list(source.get_flattened_data())
        reconstructed = Image.new("RGB", (128, 128))
        reconstructed.putdata([source_pixels[index] for index in assignments])
        assert ImageChops.difference(reconstructed, output).getbbox() is None

        target_bytes = preset_target.tobytes()
        source_error = color_error(source.tobytes(), target_bytes)
        output_error = color_error(output.tobytes(), target_bytes)
        assert output_error < source_error
        improvement = 100 * (source_error - output_error) / source_error
        print(f"{preset_name}: valid permutation, color error improved {improvement:.1f}%")


if __name__ == "__main__":
    main()
