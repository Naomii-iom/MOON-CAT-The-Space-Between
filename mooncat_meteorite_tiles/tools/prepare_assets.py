#!/usr/bin/env python3
"""Split the user-provided sprite sheet without repainting any source pixels.

The source already has real RGBA transparency.  This script only identifies
the sixteen movement poses, places them on equal transparent canvases with a
shared foot anchor, and writes a manifest for provenance/reproducibility.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pygame


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "source" / "cat_sprite_sheet_original.png"
CAT_ROOT = ROOT / "assets" / "characters" / "cat"
CANVAS_SIZE = (256, 208)
FOOT_ANCHOR = (128, 196)
ALPHA_THRESHOLD = 1


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def component_rects(sheet: pygame.Surface) -> list[pygame.Rect]:
    mask = pygame.mask.from_surface(sheet, ALPHA_THRESHOLD)
    rects: list[pygame.Rect] = []
    for component in mask.connected_components(1000):
        boxes = component.get_bounding_rects()
        if boxes:
            rects.append(boxes[0])
    # Minor anti-aliased halos give neighbouring frames slightly different
    # top coordinates, so cluster by visual row before sorting left-to-right.
    rows: list[list[pygame.Rect]] = []
    for rect in sorted(rects, key=lambda item: item.centery):
        for row in rows:
            row_center = sum(item.centery for item in row) / len(row)
            if abs(rect.centery - row_center) < 70:
                row.append(rect)
                break
        else:
            rows.append([rect])
    ordered: list[pygame.Rect] = []
    for row in rows:
        ordered.extend(sorted(row, key=lambda item: item.x))
    return ordered


def foot_anchor(sheet: pygame.Surface, rect: pygame.Rect) -> tuple[int, int]:
    """Estimate the feet from the lowest opaque band, avoiding raised tails."""
    cutoff = rect.bottom - max(18, round(rect.height * 0.16))
    xs: list[int] = []
    lowest = rect.top
    for y in range(cutoff, rect.bottom):
        for x in range(rect.left, rect.right):
            if sheet.get_at((x, y)).a > ALPHA_THRESHOLD:
                xs.append(x)
                lowest = max(lowest, y)
    if not xs:
        return rect.centerx, rect.bottom - 1
    xs.sort()
    return xs[len(xs) // 2], lowest


def place_on_canvas(
    sheet: pygame.Surface, rect: pygame.Rect, source_anchor: tuple[int, int]
) -> pygame.Surface:
    canvas = pygame.Surface(CANVAS_SIZE, pygame.SRCALPHA)
    frame = sheet.subsurface(rect).copy()
    dx = FOOT_ANCHOR[0] - (source_anchor[0] - rect.x)
    dy = FOOT_ANCHOR[1] - (source_anchor[1] - rect.y)
    target = pygame.Rect(dx, dy, rect.width, rect.height)
    if not canvas.get_rect().contains(target):
        raise ValueError(f"Frame {rect} does not fit normalized canvas at {target}")
    canvas.blit(frame, target)
    return canvas


def main() -> None:
    pygame.init()
    pygame.display.set_mode((1, 1), flags=pygame.HIDDEN)
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    sheet = pygame.image.load(str(SOURCE)).convert_alpha()
    rects = component_rects(sheet)
    if len(rects) < 16:
        raise RuntimeError(f"Expected at least 16 cat components, found {len(rects)}")

    groups = {
        "walk_down": rects[0:4],
        "walk_right": rects[4:8],
        "walk_left": rects[8:12],
        "walk_up": rects[12:16],
    }
    manifest: dict[str, object] = {
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha256(SOURCE),
        "source_size": list(sheet.get_size()),
        "source_mode": "RGBA",
        "processing": "exact crop + transparent padding + shared foot anchor; no repainting",
        "canvas_size": list(CANVAS_SIZE),
        "foot_anchor": list(FOOT_ANCHOR),
        "animations": {},
        "unused_components": [list(rect) for rect in rects[16:]],
    }

    for state, state_rects in groups.items():
        state_dir = CAT_ROOT / state
        state_dir.mkdir(parents=True, exist_ok=True)
        frames: list[dict[str, object]] = []
        for index, rect in enumerate(state_rects):
            anchor = foot_anchor(sheet, rect)
            canvas = place_on_canvas(sheet, rect, anchor)
            output = state_dir / f"{index:02d}.png"
            pygame.image.save(canvas, str(output))
            frames.append(
                {
                    "file": str(output.relative_to(ROOT)),
                    "source_rect": list(rect),
                    "source_foot_anchor": list(anchor),
                    "sha256": sha256(output),
                }
            )
        manifest["animations"][state] = frames

    idle_dir = CAT_ROOT / "idle"
    idle_dir.mkdir(parents=True, exist_ok=True)
    for index in range(4):
        shutil.copyfile(CAT_ROOT / "walk_down" / f"{index:02d}.png", idle_dir / f"{index:02d}.png")

    manifest_path = CAT_ROOT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared 16 movement frames + 4 idle copies in {CAT_ROOT}")
    print(f"Detected {len(rects)} character-sized components; {len(rects) - 16} intentionally unused")
    pygame.quit()


if __name__ == "__main__":
    main()
