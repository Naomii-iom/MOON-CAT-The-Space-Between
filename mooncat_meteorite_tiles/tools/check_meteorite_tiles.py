#!/usr/bin/env python3
"""Deterministic regression, asset and render checks for meteorite tiles."""

from __future__ import annotations

import argparse
import ast
from collections import deque
from collections import Counter
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


def canonical_node(source: str, name: str) -> str:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == name:
            return ast.dump(node, include_attributes=False)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.dump(node.value, include_attributes=False)
    raise KeyError(name)


def execute_without_loop(path: Path, load_log: list[str]) -> dict[str, object]:
    source = path.read_text(encoding="utf-8")
    prefix = source.split("running=True\nwhile running:", 1)[0]
    original_load = pygame.image.load

    def tracked_load(filename, *args, **kwargs):
        load_log.append(str(filename))
        return original_load(filename, *args, **kwargs)

    pygame.image.load = tracked_load
    namespace: dict[str, object] = {
        "__file__": str(path),
        "__name__": "mooncat_meteorite_qa",
    }
    sys.path.insert(0, str(ROOT))
    try:
        exec(compile(prefix, str(path), "exec"), namespace)
    finally:
        pygame.image.load = original_load
    return namespace


def solve_room(namespace: dict[str, object], index: int) -> tuple[int, list[str]]:
    State = namespace["State"]
    execute = namespace["execute"]
    start = State(index)
    queue = deque([(start, [])])
    visited = set()
    actions = ("up", "right", "down", "left", "q", "e")
    while queue and len(visited) < 50000:
        state, path = queue.popleft()
        key = (state.player, state.world, state.stone, state.lit, state.echo)
        if key in visited:
            continue
        visited.add(key)
        if state.exit_reached():
            return len(visited), path
        for action in actions:
            next_state = state.copy()
            changed, _, _, _ = execute(next_state, action)
            if changed:
                queue.append((next_state, path + [action]))
    raise AssertionError(f"Room {index + 1} has no solution")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    args = parser.parse_args()
    baseline_source = args.baseline.read_text(encoding="utf-8")
    baseline_root = args.baseline.resolve().parent
    current_source = (ROOT / "main.py").read_text(encoding="utf-8")

    protected = (
        "ROOMS",
        "GUIDES",
        "State",
        "execute",
        "solution_hint",
        "guide_goal",
        "load_progress",
        "save_progress",
    )
    protected_equal = {
        name: canonical_node(baseline_source, name) == canonical_node(current_source, name)
        for name in protected
    }
    assert all(protected_equal.values()), protected_equal

    required_keys = (
        "pygame.K_q",
        "pygame.K_h",
        "pygame.K_z",
        "pygame.K_r",
        "pygame.K_a",
        "pygame.K_d",
        "pygame.K_w",
        "pygame.K_s",
        "pygame.K_LEFT",
        "pygame.K_RIGHT",
        "pygame.K_UP",
        "pygame.K_DOWN",
    )
    key_mapping_present = {key: key in current_source for key in required_keys}
    assert all(key_mapping_present.values()), key_mapping_present

    pygame.init()
    pygame.display.set_mode((1, 1))
    load_log: list[str] = []
    ns = execute_without_loop(ROOT / "main.py", load_log)
    initial_loads = len(load_log)
    assert initial_loads == 34, f"Expected 2 backgrounds + 20 cat + 12 tile PNG loads, got {initial_loads}"

    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    # Background and character art are locked byte-for-byte to the preceding
    # visual-integration build.  This task may only change tile presentation.
    preserved_assets: dict[str, bool] = {}
    for folder in ("backgrounds", "characters"):
        for current_path in sorted((ROOT / "assets" / folder).rglob("*.png")):
            relative = current_path.relative_to(ROOT / "assets")
            baseline_path = baseline_root / "assets" / relative
            preserved_assets[str(relative)] = baseline_path.is_file() and digest(current_path) == digest(baseline_path)
    assert preserved_assets and all(preserved_assets.values()), preserved_assets

    tile_root = ROOT / "assets" / "tiles" / "meteorites"
    kinds = ("normal_a", "normal_b", "normal_c", "normal_d", "special", "goal")
    tile_checks: list[dict[str, object]] = []
    for kind in kinds:
        moon = pygame.image.load(str(tile_root / "moonlight" / f"{kind}.png"))
        shadow = pygame.image.load(str(tile_root / "shadow" / f"{kind}.png"))
        assert moon.get_size() == (64, 64) == shadow.get_size()
        moon_alpha = pygame.image.tobytes(moon, "RGBA")[3::4]
        shadow_alpha = pygame.image.tobytes(shadow, "RGBA")[3::4]
        assert moon_alpha == shadow_alpha, f"World silhouette drift: {kind}"
        assert min(moon_alpha) == 0 and max(moon_alpha) == 255
        tile_checks.append({
            "kind": kind,
            "size": [64, 64],
            "same_alpha_in_both_worlds": True,
        })

    # Measure the actual five-room floor set, excluding intentional special and
    # goal states.  This verifies visual restraint, not puzzle quality.
    normal_counts: Counter[str] = Counter()
    for room_index, level in enumerate(ns["ROOMS"]):
        for world in (0, 1):
            for point in level["floors"][world]:
                kind = ns["METEORITE_TILES"].kind_for(room_index, point, world, level)
                if kind.startswith("normal_"):
                    normal_counts[kind] += 1
    normal_total = sum(normal_counts.values())
    normal_a_ratio = normal_counts["normal_a"] / normal_total
    assert 0.70 <= normal_a_ratio <= 0.80, (normal_counts, normal_a_ratio)

    # Time-based floating is visual only.  Verify amplitude, exact period,
    # neighbour cohesion, world-independent phase and the runtime off switch.
    tiles = ns["METEORITE_TILES"]
    float_level = ns["ROOMS"][0]
    float_points = sorted(float_level["floors"][0] | float_level["floors"][1])
    period_ms = round(tiles.float_period_seconds * 1000)
    sample_times = [0, period_ms // 8, period_ms // 4, period_ms // 2, period_ms * 3 // 4]
    sampled_offsets = {
        str(now_ms): {
            str(point): tiles.pixel_offset(0, point, float_level, now_ms)
            for point in float_points
        }
        for now_ms in sample_times
    }
    assert max(abs(value) for offsets in sampled_offsets.values() for value in offsets.values()) <= 2
    for point in float_points:
        assert tiles.pixel_offset(0, point, float_level, 321) == tiles.pixel_offset(0, point, float_level, 321 + period_ms)
    max_neighbour_difference = 0
    point_set = set(float_points)
    for now_ms in sample_times:
        for x, y in float_points:
            for neighbour in ((x + 1, y), (x, y + 1)):
                if neighbour in point_set:
                    difference = abs(
                        tiles.pixel_offset(0, (x, y), float_level, now_ms)
                        - tiles.pixel_offset(0, neighbour, float_level, now_ms)
                    )
                    max_neighbour_difference = max(max_neighbour_difference, difference)
    assert max_neighbour_difference <= 1
    continuity_state = ns["State"](0)
    ns["current"] = continuity_state
    continuity_state.world = 0
    before_q_offset = ns["tile_bob"](continuity_state.player, 777)
    continuity_state.world = 1
    after_q_offset = ns["tile_bob"](continuity_state.player, 777)
    q_continuity = before_q_offset == after_q_offset
    assert q_continuity
    tiles.set_floating(False)
    assert all(tiles.pixel_offset(0, point, float_level, 777) == 0 for point in float_points)
    tiles.set_floating(
        ns["FLOAT_TILES_ENABLED"],
        amplitude=ns["FLOAT_TILES_AMPLITUDE"],
        period_seconds=ns["FLOAT_TILES_PERIOD_SECONDS"],
    )

    solutions: dict[str, object] = {}
    for index in range(5):
        visited, path = solve_room(ns, index)
        solutions[str(index + 1)] = {
            "solved": True,
            "visited_states": visited,
            "actions": path,
        }

    cat_files = sorted((ROOT / "assets" / "characters" / "cat").glob("*/*.png"))
    assert len(cat_files) == 20
    cat_checks = []
    for path in cat_files:
        frame = pygame.image.load(str(path))
        assert frame.get_size() == (256, 208)
        assert frame.get_at((0, 0)).a == 0
        assert frame.get_at((255, 207)).a == 0
        cat_checks.append({"file": str(path.relative_to(ROOT)), "size": list(frame.get_size())})

    ns["mode"] = "play"
    ns["guide_open"] = False
    ns["WORLD_TRANSITION"].cancel()
    ns["current"] = ns["State"](0)
    ns["CAT_MOTION"].reset(ns["tile_center"](ns["current"].player), "down")
    ns["render"]()
    moon_path = ROOT / "screenshots" / "moonlight_true_render.png"
    pygame.image.save(ns["screen"], str(moon_path))
    board_crop = ns["screen"].subsurface(ns["BOARD_RECT"]).copy()
    board_zoom = pygame.transform.scale(board_crop, (board_crop.get_width() * 2, board_crop.get_height() * 2))
    pygame.image.save(board_zoom, str(ROOT / "screenshots" / "meteorite_layout_zoom.png"))

    ns["player_action"]("q")
    assert ns["current"].world == 1
    assert ns["WORLD_TRANSITION"].is_active()
    ns["WORLD_TRANSITION"].started_ms -= 260
    ns["render"]()
    pygame.image.save(ns["screen"], str(ROOT / "screenshots" / "world_transition_midpoint.png"))
    ns["WORLD_TRANSITION"].started_ms -= 400
    ns["render"]()
    assert not ns["WORLD_TRANSITION"].is_active()
    pygame.image.save(ns["screen"], str(ROOT / "screenshots" / "shadow_true_render.png"))

    # Invalid Q: no new transition and no world-state change.
    ns["current"] = ns["State"](0)
    ns["current"].player = (13, 2)
    ns["current"].world = 0
    ns["WORLD_TRANSITION"].cancel()
    ns["render"]()
    ns["player_action"]("q")
    assert ns["current"].world == 0
    assert not ns["WORLD_TRANSITION"].is_active()

    # Render repeatedly and prove assets are not read again per frame.
    render_times = []
    for _ in range(180):
        started = time.perf_counter()
        ns["render"]()
        render_times.append((time.perf_counter() - started) * 1000)
    assert len(load_log) == initial_loads

    report = {
        "result": "pass",
        "resolution": [ns["WIDTH"], ns["HEIGHT"]],
        "grid": {"columns": ns["COLS"], "rows": ns["ROWS"], "tile": ns["TILE"]},
        "protected_logic_ast_equal": protected_equal,
        "key_mapping_present": key_mapping_present,
        "startup_png_loads": initial_loads,
        "png_loads_after_180_renders": len(load_log),
        "tile_pngs": tile_checks,
        "normal_variant_counts": dict(sorted(normal_counts.items())),
        "normal_a_ratio": round(normal_a_ratio, 4),
        "floating_animation": {
            "enabled": tiles.floating_enabled,
            "amplitude_pixels": tiles.float_amplitude,
            "period_seconds": tiles.float_period_seconds,
            "phase_step_radians": tiles.phase_step,
            "group_span_tiles": tiles.group_span,
            "max_sampled_neighbour_difference_pixels": max_neighbour_difference,
            "same_phase_through_q": q_continuity,
            "runtime_disable_test": "pass",
        },
        "preserved_background_and_cat_assets": preserved_assets,
        "background_source_sizes": [list(size) for size in ns["BACKGROUNDS"].source_sizes],
        "background_cover_crops": [list(rect) for rect in ns["BACKGROUNDS"].crop_rects],
        "cat_frames": cat_checks,
        "world_transition_ms": ns["WORLD_TRANSITION"].duration_ms,
        "move_interpolation_ms": ns["CAT_MOTION"].duration_ms,
        "invalid_q_kept_world": True,
        "solutions": solutions,
        "offscreen_render_ms": {
            "median": round(statistics.median(render_times), 3),
            "p95": round(sorted(render_times)[round(len(render_times) * 0.95) - 1], 3),
        },
        "limits": [
            "Offscreen timing is a regression indicator, not a native-window or browser FPS measurement.",
            "Browser interaction is recorded separately in browser_test_result.json.",
        ],
    }
    output = ROOT / "screenshots" / "verification.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    pygame.quit()


if __name__ == "__main__":
    main()
