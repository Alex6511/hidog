#!/usr/bin/env python3
"""Generate Hidog's derived target and icon assets from the vendored sticker."""

from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src" / "app" / "calculate" / "target.webp"
EXPECTED_SHA256 = "7e66af0630b5781a4606f98f4800431257eac10d235448d295798c6812f449cc"
PRESET_NAMES = ("wisetree", "blackhole", "cat", "cat2", "colorful")


def fitted(image: Image.Image, size: int) -> Image.Image:
    return ImageOps.fit(
        image,
        (size, size),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )


def main() -> None:
    digest = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(f"unexpected target SHA-256: {digest}")

    with Image.open(TARGET) as source:
        if source.size != (233, 240) or getattr(source, "n_frames", 1) != 1:
            raise SystemExit(f"unexpected target properties: {source.size}, {source.n_frames} frames")
        dog = source.convert("RGB")

    dog_128 = fitted(dog, 128)
    dog_256 = fitted(dog, 256)

    calculate_dir = ROOT / "src" / "app" / "calculate"
    dog_128.save(calculate_dir / "target128.png", optimize=True)
    dog_256.save(calculate_dir / "target256.png", optimize=True)
    Image.new("RGB", (128, 128), "white").save(calculate_dir / "weights128.png", optimize=True)
    Image.new("RGB", (256, 256), "white").save(calculate_dir / "weights256.png", optimize=True)

    for preset_name in PRESET_NAMES:
        dog_128.save(ROOT / "presets" / preset_name / "target.png", optimize=True)

    assets = ROOT / "assets"
    for filename, size in (
        ("favicon-16x16.png", 16),
        ("favicon-32x32.png", 32),
        ("apple-touch-icon.png", 180),
        ("android-chrome-192x192.png", 192),
        ("android-chrome-512x512.png", 512),
        ("icon128.png", 128),
    ):
        fitted(dog, size).save(assets / filename, optimize=True)

    fitted(dog, 256).save(
        assets / "favicon.ico",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    fitted(dog, 512).save(assets / "linux" / "icon.png", optimize=True)
    fitted(dog, 1024).save(
        assets / "macos" / "icon.icns",
        sizes=[(16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512), (1024, 1024)],
    )


if __name__ == "__main__":
    main()
