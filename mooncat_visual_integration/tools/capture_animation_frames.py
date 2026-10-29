#!/usr/bin/env python3
"""Render short, real-game animation sequences for preview assembly."""

from __future__ import annotations

import os
from pathlib import Path
import sys
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


ROOT = Path(__file__).resolve().parents[1]


def load_game() -> dict[str, object]:
    source = (ROOT / "main.py").read_text(encoding="utf-8")
    prefix = source.split("running=True\nwhile running:", 1)[0]
    sys.path.insert(0, str(ROOT))
    namespace: dict[str, object] = {
        "__file__": str(ROOT / "main.py"),
        "__name__": "mooncat_preview_capture",
    }
    exec(compile(prefix, str(ROOT / "main.py"), "exec"), namespace)
    namespace["mode"] = "play"
    namespace["guide_open"] = False
    return namespace


def save_board(namespace: dict[str, object], path: Path) -> None:
    board_rect = namespace["BOARD_RECT"]
    board = namespace["screen"].subsurface(board_rect).copy()
    pygame.image.save(board, str(path))


def capture_walk(namespace: dict[str, object], directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    namespace["current"] = namespace["State"](0)
    namespace["current"].player = (1, 4)
    namespace["CAT_MOTION"].reset(namespace["tile_center"]((1, 4)), "right")
    index = 0
    for _ in range(5):
        namespace["player_action"]("right")
        for _ in range(5):
            namespace["render"]()
            save_board(namespace, directory / f"{index:03d}.png")
            index += 1
            time.sleep(0.034)
    for _ in range(5):
        namespace["render"]()
        save_board(namespace, directory / f"{index:03d}.png")
        index += 1
        time.sleep(0.05)


def capture_transition(namespace: dict[str, object], directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    namespace["current"] = namespace["State"](0)
    namespace["CAT_MOTION"].reset(namespace["tile_center"](namespace["current"].player), "down")
    namespace["WORLD_TRANSITION"].cancel()
    namespace["render"]()
    namespace["player_action"]("q")
    for index in range(13):
        namespace["render"]()
        pygame.image.save(namespace["screen"], str(directory / f"{index:03d}.png"))
        time.sleep(0.045)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: capture_animation_frames.py OUTPUT_DIRECTORY")
    output = Path(sys.argv[1]).resolve()
    pygame.init()
    pygame.display.set_mode((1, 1))
    namespace = load_game()
    capture_walk(namespace, output / "walk")
    capture_transition(namespace, output / "transition")
    print(output)
    pygame.quit()


if __name__ == "__main__":
    main()
