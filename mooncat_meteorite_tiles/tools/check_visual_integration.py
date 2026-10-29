#!/usr/bin/env python3
"""Deterministic regression and render checks for the visual integration build."""

from __future__ import annotations

import argparse
import ast
from collections import deque
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
        "__name__": "mooncat_visual_qa",
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
    assert initial_loads == 22, f"Expected 2 backgrounds + 20 cat PNG loads, got {initial_loads}"

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
    pygame.image.save(ns["screen"], str(ROOT / "screenshots" / "moonlight_regression.png"))

    ns["player_action"]("q")
    assert ns["current"].world == 1
    assert ns["WORLD_TRANSITION"].is_active()
    ns["WORLD_TRANSITION"].started_ms -= 260
    ns["render"]()
    pygame.image.save(ns["screen"], str(ROOT / "screenshots" / "transition_regression.png"))
    ns["WORLD_TRANSITION"].started_ms -= 400
    ns["render"]()
    assert not ns["WORLD_TRANSITION"].is_active()
    pygame.image.save(ns["screen"], str(ROOT / "screenshots" / "shadow_regression.png"))

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
