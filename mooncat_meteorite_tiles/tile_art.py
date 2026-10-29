"""Cached, presentation-only meteorite tiles for MOON CAT.

This module never changes floor membership, collision, puzzle state, controls,
or saves.  It maps an existing logical tile to a stable visual variant.
"""

from __future__ import annotations

from collections import deque
import math
from pathlib import Path

import pygame


class MeteoriteTiles:
    WORLD_NAMES = ("moonlight", "shadow")
    KINDS = ("normal_a", "normal_b", "normal_c", "normal_d", "special", "goal")

    def __init__(
        self,
        root: Path,
        tile_size: int,
        *,
        floating_enabled: bool = True,
        float_amplitude: float = 1.5,
        float_period_seconds: float = 3.4,
        phase_step: float = 0.16,
        group_span: int = 4,
    ) -> None:
        self.root = root
        self.tile_size = tile_size
        self.floating_enabled = floating_enabled
        self.float_amplitude = float_amplitude
        self.float_period_seconds = float_period_seconds
        self.phase_step = phase_step
        self.group_span = group_span
        self.loaded_files: list[Path] = []
        self.sprites: dict[int, dict[str, pygame.Surface]] = {0: {}, 1: {}}
        self.previews: dict[int, dict[str, pygame.Surface]] = {0: {}, 1: {}}
        self._phase_cache: dict[tuple[int, frozenset[tuple[int, int]]], dict[tuple[int, int], float]] = {}
        preview_colours = ((104, 215, 243), (247, 132, 176))

        self.shadow = pygame.Surface((tile_size, tile_size + 6), pygame.SRCALPHA)
        pygame.draw.ellipse(
            self.shadow,
            (4, 7, 20, 28),
            (round(tile_size * 0.16), round(tile_size * 0.76), round(tile_size * 0.68), 6),
        )

        for world, folder in enumerate(self.WORLD_NAMES):
            for kind in self.KINDS:
                path = root / folder / f"{kind}.png"
                if not path.is_file():
                    raise FileNotFoundError(f"Meteorite tile PNG is missing: {path}")
                self.loaded_files.append(path)
                source = pygame.image.load(str(path)).convert_alpha()
                # Scale exactly once.  Nearest-neighbour keeps the soft pixel art
                # legible and avoids per-frame image work.
                sprite = pygame.transform.scale(source, (tile_size, tile_size)).convert_alpha()
                self.sprites[world][kind] = sprite
                self.previews[world][kind] = self._make_preview(sprite, preview_colours[world])

    @staticmethod
    def _make_preview(sprite: pygame.Surface, colour: tuple[int, int, int]) -> pygame.Surface:
        """Create a cached faint silhouette for tiles that exist in the other world."""
        mask = pygame.mask.from_surface(sprite, 48)
        preview = mask.to_surface(
            setcolor=(*colour, 30),
            unsetcolor=(0, 0, 0, 0),
        ).convert_alpha()
        outline = mask.outline()
        if len(outline) > 2:
            pygame.draw.lines(preview, (*colour, 92), True, outline, 1)
        return preview

    @staticmethod
    def normal_variant(room_index: int, point: tuple[int, int]) -> str:
        """Stable 75/10/10/5 distribution; independent from frame and world."""
        x, y = point
        value = (x * 37 + y * 19 + room_index * 13) % 20
        if value < 15:
            return "normal_a"
        if value < 17:
            return "normal_b"
        if value < 19:
            return "normal_c"
        return "normal_d"

    def kind_for(
        self,
        room_index: int,
        point: tuple[int, int],
        world: int,
        level: dict,
    ) -> str:
        if point == level["exit"] and world == level["exit_world"]:
            return "goal"
        if point == level.get("plate") and world == level.get("plate_world"):
            return "special"
        if point == level.get("gate") and world == level.get("gate_world"):
            return "special"
        if point == level.get("lantern") and world == 0:
            return "special"
        return self.normal_variant(room_index, point)

    def set_floating(
        self,
        enabled: bool,
        *,
        amplitude: float | None = None,
        period_seconds: float | None = None,
    ) -> None:
        """Adjust or disable idle bobbing without touching logical tile state."""
        self.floating_enabled = enabled
        if amplitude is not None:
            self.float_amplitude = max(0.0, float(amplitude))
        if period_seconds is not None:
            self.float_period_seconds = max(0.1, float(period_seconds))

    def _phase_map(self, room_index: int, level: dict) -> dict[tuple[int, int], float]:
        # Use the union of both worlds, so the same coordinate keeps its phase
        # through Q.  Four-step BFS bands share a phase; adjacent bands differ
        # only slightly, keeping roads visually joined instead of wobbling apart.
        points = frozenset(level["floors"][0] | level["floors"][1])
        cache_key = (room_index, points)
        if cache_key in self._phase_cache:
            return self._phase_cache[cache_key]

        remaining = set(points)
        phases: dict[tuple[int, int], float] = {}
        component_index = 0
        while remaining:
            anchor = min(remaining, key=lambda point: (point[1], point[0]))
            queue = deque([(anchor, 0)])
            remaining.remove(anchor)
            base_phase = (room_index * 0.53 + component_index * 0.71) % math.tau
            while queue:
                point, distance = queue.popleft()
                phases[point] = base_phase + (distance // self.group_span) * self.phase_step
                x, y = point
                for neighbour in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if neighbour in remaining:
                        remaining.remove(neighbour)
                        queue.append((neighbour, distance + 1))
            component_index += 1
        self._phase_cache[cache_key] = phases
        return phases

    def bob_offset(
        self,
        room_index: int,
        point: tuple[int, int],
        level: dict,
        now_ms: int | None = None,
    ) -> float:
        if not self.floating_enabled or self.float_amplitude <= 0:
            return 0.0
        now_ms = pygame.time.get_ticks() if now_ms is None else now_ms
        phase = self._phase_map(room_index, level).get(point, room_index * 0.53)
        angle = math.tau * (now_ms / 1000.0) / self.float_period_seconds + phase
        return self.float_amplitude * math.sin(angle)

    def pixel_offset(
        self,
        room_index: int,
        point: tuple[int, int],
        level: dict,
        now_ms: int | None = None,
    ) -> int:
        return round(self.bob_offset(room_index, point, level, now_ms))

    def draw(
        self,
        target: pygame.Surface,
        position: tuple[int, int],
        world: int,
        kind: str,
        y_offset: int = 0,
    ) -> None:
        x, y = position
        # The shadow moves only a fraction of the sprite distance, creating a
        # quiet sense of depth without looking like a glow or separate platform.
        target.blit(self.shadow, (x, y + round(y_offset * 0.2)))
        target.blit(self.sprites[world][kind], (x, y + y_offset))

    def draw_preview(
        self,
        target: pygame.Surface,
        position: tuple[int, int],
        world: int,
        kind: str,
        y_offset: int = 0,
    ) -> None:
        x, y = position
        target.blit(self.previews[world][kind], (x, y + y_offset))
