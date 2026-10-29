"""Check the background integration without running or saving original games.

Usage: python tools/check_art.py /path/to/backups/MOON_CAT_Guided_v1.py
The screenshots from this script are explicitly OFFSCREEN pygame renders.
Interactive browser screenshots are captured separately.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(sys.argv[1]).resolve()


def dump(node):
    return ast.dump(node, include_attributes=False)


def load_definitions(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    # Keep real game's startup and definitions; stop before its normal loop.
    stop = next(i for i, n in enumerate(tree.body) if isinstance(n, ast.While))
    return tree, ast.Module(body=tree.body[:stop], type_ignores=[])


original, _ = load_definitions(BASELINE)
modified, definitions = load_definitions(ROOT / "main.py")
original_functions = {n.name: n for n in original.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
modified_functions = {n.name: n for n in modified.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
for name, node in original_functions.items():
    if name in ("draw_backdrop", "draw_board"):
        continue
    assert dump(node) == dump(modified_functions[name]), f"Unexpected change: {name}"
assert [dump(n) for n in original_functions["draw_board"].body[4:]] == [
    dump(n) for n in modified_functions["draw_board"].body[4:]
], "Board content changed beyond its background"

# Apart from background startup and the docstring/import, every top-level node
# (maps, palettes, saves, input/main loop, and all gameplay code) must match.
def invariant_nodes(tree):
    nodes = []
    for i, node in enumerate(tree.body):
        if i == 0 or isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(node, ast.FunctionDef) and node.name in ("draw_backdrop", "draw_board"):
            continue
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "MOONLIGHT_ART" for t in node.targets):
            continue
        nodes.append(dump(node))
    return nodes

assert invariant_nodes(original) == invariant_nodes(modified), "Non-background code changed"

sys.path.insert(0, str(ROOT))
loads = []
real_load = pygame.image.load


def tracked_load(filename, *args, **kwargs):
    loads.append(str(filename))
    return real_load(filename, *args, **kwargs)


pygame.image.load = tracked_load
game = {"__name__": "art_render_check", "__file__": str(ROOT / "main.py")}
exec(compile(definitions, str(ROOT / "main.py"), "exec"), game)
game["begin"](0)
game["guide_open"] = False
game["notice_ttl"] = 0
game["render"]()
pygame.image.save(game["screen"], str(ROOT / "screenshots" / "moonlight_offscreen_render.png"))

timings = []
for _ in range(180):
    start = time.perf_counter()
    game["render"]()
    timings.append((time.perf_counter() - start) * 1000)
assert len(loads) == 1, f"PNG reloaded {len(loads)} times"
assert game["MOONLIGHT_ART"].scene.get_size() == (1060, 735)
assert game["MOONLIGHT_ART"].board.get_at((0, 0)).a == 0
assert game["MOONLIGHT_ART"].board.get_at((100, 100)).a == 255

# Pixel-level regression: UI panels, road, cat and exit must be exactly the same
# when the original renderer is used on identical time/state/random seed.
import random
from unittest.mock import patch
baseline_game = {"__name__": "baseline_render_check", "__file__": str(BASELINE)}
_, baseline_definitions = load_definitions(BASELINE)
exec(compile(baseline_definitions, str(BASELINE), "exec"), baseline_game)
for namespace in (baseline_game, game):
    namespace["begin"](0)
    namespace["guide_open"] = False
    namespace["notice_ttl"] = 0
    namespace["phase_flash"] = 0
    namespace["shakes"] = 0
    namespace["memories"] = set()
    namespace["unlocked"] = 1

regions = {
    # Exclude rounded transparent corners, where the changed background is
    # intentionally visible. Compare solid interiors and actual foreground.
    "top_room_label_interior": (355, 44, 240, 28),
    "sidebar_interior": (768, 184, 236, 378),
    "bottom_ui_interior": (56, 606, 950, 80),
    "road_tile_interior": (277, 356, 32, 32),
    "cat_on_tile_interior": (145, 444, 32, 32),
    "exit_on_tile_interior": (629, 268, 32, 32),
}
with patch.object(pygame.time, "get_ticks", return_value=1000):
    baseline_game["render"]()
    baseline_pixels = {name: pygame.image.tobytes(baseline_game["screen"].subsurface(rect), "RGB") for name, rect in regions.items()}
    game["render"]()
    for name, rect in regions.items():
        art_pixels = pygame.image.tobytes(game["screen"].subsurface(rect), "RGB")
        assert art_pixels == baseline_pixels[name], f"Original foreground changed: {name}"

report = {
    "baseline": str(BASELINE),
    "baseline_sha256": hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
    "background_png_loads_in_180_frames": len(loads),
    "source_image_size": game["MOONLIGHT_ART"].source_size,
    "render_size": game["screen"].get_size(),
    "board_cached_alpha_corners": "transparent; interior opaque",
    "unchanged_ast": "all maps, gameplay, input, saves, character, UI and palette code",
    "unchanged_pixels": list(regions),
    "offscreen_render_ms_median": round(statistics.median(timings), 3),
    "offscreen_render_ms_p95": round(sorted(timings)[int(len(timings) * .95)], 3),
    "performance_limit": "CPU offscreen rendering only; not native window FPS or browser FPS",
}
(ROOT / "screenshots" / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
pygame.quit()
