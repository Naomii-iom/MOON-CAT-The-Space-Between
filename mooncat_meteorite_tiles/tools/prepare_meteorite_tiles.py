#!/usr/bin/env python3
"""Prepare deterministic MOON CAT meteorite tile sprites from the supplied sheet.

This script does not generate or redraw artwork.  It isolates six existing
shapes, removes chromatic fringe/background residue, normalizes their canvas,
and makes two colour variants while preserving each source silhouette.
"""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
TILE_ROOT = ROOT / "assets" / "tiles" / "meteorites"
SOURCE = TILE_ROOT / "original_sheet.png"
CANVAS_SIZE = 64
CONTENT_SIZE = 60

# Bounding rectangles were measured from connected opaque components in the
# supplied non-grid sheet.  They deliberately select only clean, useful forms.
SELECTIONS = {
    "normal_a": {"bbox": (77, 73, 176, 183), "role": "common crater tile"},
    "normal_b": {"bbox": (296, 73, 175, 182), "role": "light crater variation"},
    "normal_c": {"bbox": (77, 288, 175, 182), "role": "fine crack variation"},
    "normal_d": {"bbox": (1167, 63, 183, 192), "role": "attached-rock edge variation"},
    "special": {"bbox": (950, 288, 176, 182), "role": "subtle sparkle base"},
    "goal": {"bbox": (80, 513, 176, 183), "role": "portal ring base"},
}

# Five-stop ramps retain source lighting and crater geometry without inventing
# detail.  The exact same alpha/silhouette is used in both worlds.
PALETTES = {
    "moonlight": [
        (24, 29, 55),
        (47, 59, 91),
        (83, 104, 137),
        (135, 160, 190),
        (205, 217, 232),
    ],
    "shadow": [
        (31, 21, 47),
        (59, 39, 76),
        (106, 72, 118),
        (164, 110, 149),
        (226, 169, 196),
    ],
}


def is_fringe(pixel: tuple[int, int, int, int]) -> bool:
    """Identify the sheet's electric magenta/blue residue, not soft pink art."""
    r, g, b, a = pixel
    if a == 0:
        return False
    magenta = r > 175 and b > 125 and g < 95 and r - g > 90 and b - g > 60
    electric_blue = b > 145 and r < 100 and g < 145 and b - r > 70
    return magenta or electric_blue


def largest_component(mask: list[list[bool]]) -> set[tuple[int, int]]:
    height = len(mask)
    width = len(mask[0])
    seen: set[tuple[int, int]] = set()
    best: set[tuple[int, int]] = set()
    for y in range(height):
        for x in range(width):
            if not mask[y][x] or (x, y) in seen:
                continue
            component: set[tuple[int, int]] = set()
            queue = deque([(x, y)])
            seen.add((x, y))
            while queue:
                px, py = queue.popleft()
                component.add((px, py))
                for nx, ny in ((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)):
                    if 0 <= nx < width and 0 <= ny < height and mask[ny][nx] and (nx, ny) not in seen:
                        seen.add((nx, ny))
                        queue.append((nx, ny))
            if len(component) > len(best):
                best = component
    return best


def clean_cutout(sheet: Image.Image, rect: tuple[int, int, int, int]) -> Image.Image:
    x, y, width, height = rect
    pad = 10
    crop = sheet.crop((x - pad, y - pad, x + width + pad, y + height + pad)).convert("RGBA")
    pixels = crop.load()
    seed_mask = [
        [pixels[px, py][3] >= 96 and not is_fringe(pixels[px, py]) for px in range(crop.width)]
        for py in range(crop.height)
    ]
    component = largest_component(seed_mask)
    if not component:
        raise RuntimeError(f"No usable sprite component found for {rect}")

    core = Image.new("L", crop.size, 0)
    core_pixels = core.load()
    for px, py in component:
        core_pixels[px, py] = 255
    # Retain only a small anti-aliased collar around the actual tile.  Detached
    # splashes and sheet residue disappear, while the soft supplied edge stays.
    permitted = core.filter(ImageFilter.MaxFilter(7))
    permitted_pixels = permitted.load()
    cleaned = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    out = cleaned.load()
    for py in range(crop.height):
        for px in range(crop.width):
            original = pixels[px, py]
            if permitted_pixels[px, py] and not is_fringe(original):
                # Very faint source pixels are background haze rather than edge.
                alpha = original[3] if original[3] >= 12 else 0
                out[px, py] = (*original[:3], alpha)

    alpha = cleaned.getchannel("A")
    bounds = alpha.getbbox()
    if bounds is None:
        raise RuntimeError(f"Cutout became empty for {rect}")
    cleaned = cleaned.crop(bounds)

    scale = min(CONTENT_SIZE / cleaned.width, CONTENT_SIZE / cleaned.height)
    new_size = (max(1, round(cleaned.width * scale)), max(1, round(cleaned.height * scale)))
    cleaned = cleaned.resize(new_size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
    offset = ((CANVAS_SIZE - new_size[0]) // 2, (CANVAS_SIZE - new_size[1]) // 2)
    canvas.alpha_composite(cleaned, offset)
    # LANCZOS can blend a removed fringe colour into a handful of edge pixels;
    # run the same conservative chroma check once more on the final canvas.
    final_pixels = canvas.load()
    for py in range(CANVAS_SIZE):
        for px in range(CANVAS_SIZE):
            if is_fringe(final_pixels[px, py]):
                final_pixels[px, py] = (0, 0, 0, 0)
    return canvas


def interpolate_palette(level: float, stops: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    level = max(0.0, min(1.0, level))
    scaled = level * (len(stops) - 1)
    index = min(len(stops) - 2, int(scaled))
    amount = scaled - index
    return tuple(round(stops[index][channel] * (1 - amount) + stops[index + 1][channel] * amount) for channel in range(3))


def recolour(source: Image.Image, palette: list[tuple[int, int, int]]) -> Image.Image:
    result = Image.new("RGBA", source.size, (0, 0, 0, 0))
    src = source.load()
    dst = result.load()
    for y in range(source.height):
        for x in range(source.width):
            r, g, b, a = src[x, y]
            if a == 0:
                continue
            # Perceived luminance preserves craters, cracks and supplied shading.
            light = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
            # A small contrast lift keeps the 44 px in-game tile readable.
            light = max(0.0, min(1.0, (light - 0.08) / 0.84))
            dst[x, y] = (*interpolate_palette(light, palette), a)
    return result


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_preview(images: dict[str, dict[str, Image.Image]]) -> Image.Image:
    names = list(SELECTIONS)
    cell_w, cell_h = 154, 174
    preview = Image.new("RGBA", (cell_w * len(names), 54 + cell_h * 2), (12, 17, 36, 255))
    draw = ImageDraw.Draw(preview)
    title_font = font(22)
    label_font = font(14)
    draw.text((24, 16), "MOON CAT — METEORITE TILE SET", fill=(235, 240, 255, 255), font=title_font)
    for row, world in enumerate(("moonlight", "shadow")):
        y0 = 54 + row * cell_h
        row_colour = (104, 215, 243, 255) if world == "moonlight" else (247, 132, 176, 255)
        for column, name in enumerate(names):
            x0 = column * cell_w
            draw.rounded_rectangle((x0 + 7, y0 + 7, x0 + cell_w - 7, y0 + cell_h - 7), 14, fill=(20, 28, 51, 255), outline=(54, 68, 99, 255), width=2)
            large = images[world][name].resize((128, 128), Image.Resampling.NEAREST)
            preview.alpha_composite(large, (x0 + 13, y0 + 12))
            draw.text((x0 + cell_w // 2, y0 + 145), name.replace("_", " ").upper(), fill=row_colour, anchor="mm", font=label_font)
    return preview


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    sheet = Image.open(SOURCE).convert("RGBA")
    images: dict[str, dict[str, Image.Image]] = {"moonlight": {}, "shadow": {}}
    source_cutouts = TILE_ROOT / "source_cutouts"
    source_cutouts.mkdir(parents=True, exist_ok=True)

    for name, spec in SELECTIONS.items():
        cleaned = clean_cutout(sheet, spec["bbox"])
        cleaned.save(source_cutouts / f"{name}.png", optimize=True)
        for world, palette in PALETTES.items():
            output = recolour(cleaned, palette)
            target = TILE_ROOT / world / f"{name}.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            output.save(target, optimize=True)
            images[world][name] = output

    preview = make_preview(images)
    preview.save(TILE_ROOT / "tile_variants_preview.png", optimize=True)
    manifest = {
        "source": SOURCE.name,
        "source_size": list(sheet.size),
        "canvas_size": [CANVAS_SIZE, CANVAS_SIZE],
        "content_max_size": [CONTENT_SIZE, CONTENT_SIZE],
        "processing": [
            "manual connected-component selections from the irregular sheet",
            "electric magenta/blue fringe removal",
            "largest-silhouette isolation with a three-pixel antialias collar",
            "centred transparent 64x64 canvas",
            "luminance-preserving deterministic two-world recolour",
        ],
        "selections": SELECTIONS,
        "palettes": PALETTES,
    }
    (TILE_ROOT / "selection_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(SELECTIONS)} shapes x {len(PALETTES)} worlds")
    print(TILE_ROOT / "tile_variants_preview.png")


if __name__ == "__main__":
    main()
