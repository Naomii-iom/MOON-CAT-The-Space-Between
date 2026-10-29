#!/usr/bin/env python3
"""Assemble Pygame-rendered PNG sequences into compact review GIFs."""

from __future__ import annotations

from pathlib import Path
import sys

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


def assemble(source: Path, output: Path, *, duration: int, resize: tuple[int, int] | None = None) -> None:
    frames = []
    for path in sorted(source.glob("*.png")):
        frame = Image.open(path).convert("RGB")
        if resize:
            frame = frame.resize(resize, Image.Resampling.LANCZOS)
        frames.append(frame)
    if not frames:
        raise RuntimeError(f"No frames found in {source}")
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        optimize=True,
        disposal=2,
    )


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: assemble_previews.py FRAME_DIRECTORY")
    source = Path(sys.argv[1]).resolve()
    screenshots = ROOT / "screenshots"
    assemble(source / "walk", screenshots / "cat_walk_preview.gif", duration=50)
    assemble(
        source / "transition",
        screenshots / "world_transition_preview.gif",
        duration=55,
        resize=(848, 588),
    )
    print(screenshots / "cat_walk_preview.gif")
    print(screenshots / "world_transition_preview.gif")


if __name__ == "__main__":
    main()
