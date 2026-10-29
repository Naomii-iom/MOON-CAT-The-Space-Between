#!/usr/bin/env python3
"""Capture real pygame frames for the floating-tile acceptance GIF."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


ROOT = Path(__file__).resolve().parents[1]


def execute_without_loop(path: Path) -> dict[str, object]:
    source = path.read_text(encoding="utf-8")
    prefix = source.split("running=True\nwhile running:", 1)[0]
    namespace: dict[str, object] = {
        "__file__": str(path),
        "__name__": "mooncat_floating_capture",
    }
    sys.path.insert(0, str(ROOT))
    exec(compile(prefix, str(path), "exec"), namespace)
    return namespace


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("frame_dir", type=Path)
    parser.add_argument("--fps", type=int, default=12)
    parser.add_argument("--frames", type=int, default=60)
    args = parser.parse_args()
    args.frame_dir.mkdir(parents=True, exist_ok=True)

    pygame.init()
    pygame.display.set_mode((1, 1))
    ns = execute_without_loop(ROOT / "main.py")
    ns["mode"] = "play"
    ns["guide_open"] = False
    ns["current"] = ns["State"](0)
    ns["WORLD_TRANSITION"].cancel()
    ns["CAT_MOTION"].reset(ns["tile_center"](ns["current"].player), "down")
    clock = pygame.time.Clock()

    for frame_index in range(args.frames):
        # Idle first, then one short up/down walk, then a real legal Q switch.
        if frame_index == 24:
            ns["player_action"]("up")
        elif frame_index == 30:
            ns["player_action"]("down")
        elif frame_index == 38:
            ns["player_action"]("q")
        ns["render"]()
        board = ns["screen"].subsurface(ns["BOARD_RECT"]).copy()
        pygame.image.save(board, str(args.frame_dir / f"frame_{frame_index:03}.png"))
        clock.tick(args.fps)

    print(f"Captured {args.frames} real pygame frames at {args.fps} FPS: {args.frame_dir}")
    pygame.quit()


if __name__ == "__main__":
    main()
