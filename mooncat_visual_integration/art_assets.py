"""Cached visual assets and presentation-only animation for MOON CAT.

This module owns no puzzle rules, collision, save data, or input mapping.
"""

from __future__ import annotations

from pathlib import Path

import pygame


def _cover(image: pygame.Surface, size: tuple[int, int]) -> tuple[pygame.Surface, pygame.Rect]:
    """Scale to cover without distortion, then crop from the centre."""
    target_w, target_h = size
    source_w, source_h = image.get_size()
    scale = max(target_w / source_w, target_h / source_h)
    scaled_size = (round(source_w * scale), round(source_h * scale))
    scaled = pygame.transform.smoothscale(image, scaled_size).convert()
    crop = pygame.Rect(
        max(0, (scaled_size[0] - target_w) // 2),
        max(0, (scaled_size[1] - target_h) // 2),
        target_w,
        target_h,
    )
    return scaled.subsurface(crop).copy().convert(), crop


class WorldBackgrounds:
    """Load, resize, and prepare both user-provided worlds once."""

    def __init__(
        self,
        moonlight_path: Path,
        shadow_path: Path,
        size: tuple[int, int],
        board_rect: pygame.Rect,
    ) -> None:
        for path in (moonlight_path, shadow_path):
            if not path.is_file():
                raise FileNotFoundError(f"Background PNG is missing: {path}")
        self.paths = (moonlight_path, shadow_path)
        self.source_sizes: list[tuple[int, int]] = []
        self.crop_rects: list[pygame.Rect] = []
        self.scenes: list[pygame.Surface] = []
        self.boards: list[pygame.Surface] = []
        self.board_rect = board_rect.copy()

        washes = ((7, 16, 39, 184), (37, 14, 48, 188))
        for world, path in enumerate(self.paths):
            source = pygame.image.load(str(path)).convert()
            self.source_sizes.append(source.get_size())
            scene, crop = _cover(source, size)
            self.scenes.append(scene)
            self.crop_rects.append(crop)

            board = scene.subsurface(self.board_rect).copy().convert_alpha()
            wash = pygame.Surface(self.board_rect.size, pygame.SRCALPHA)
            wash.fill(washes[world])
            board.blit(wash, (0, 0))
            mask = pygame.Surface(self.board_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=20)
            board.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.boards.append(board)

    def draw_scene(self, target: pygame.Surface, world: int) -> None:
        target.blit(self.scenes[world], (0, 0))

    def draw_board(self, target: pygame.Surface, world: int) -> None:
        target.blit(self.boards[world], self.board_rect.topleft)


class CatSprites:
    """Load normalized sprite frames once and expose direction-aware drawing."""

    DIRECTIONS = ("down", "right", "left", "up")

    def __init__(self, cat_root: Path, display_size: tuple[int, int] = (64, 52)) -> None:
        self.cat_root = cat_root
        self.display_size = display_size
        self.frames: dict[str, list[pygame.Surface]] = {}
        self.loaded_files: list[Path] = []
        for direction in self.DIRECTIONS:
            folder = cat_root / f"walk_{direction}"
            paths = sorted(folder.glob("*.png"))
            if len(paths) != 4:
                raise FileNotFoundError(f"Expected four frames in {folder}, found {len(paths)}")
            self.frames[direction] = [self._load_frame(path) for path in paths]
        idle_paths = sorted((cat_root / "idle").glob("*.png"))
        if len(idle_paths) != 4:
            raise FileNotFoundError(f"Expected four idle frames in {cat_root / 'idle'}")
        self.idle = [self._load_frame(path) for path in idle_paths]

        # Normalized source anchor (128, 196) on a 256 x 208 canvas.
        self.anchor = (
            round(128 / 256 * display_size[0]),
            round(196 / 208 * display_size[1]),
        )

    def _load_frame(self, path: Path) -> pygame.Surface:
        self.loaded_files.append(path)
        source = pygame.image.load(str(path)).convert_alpha()
        # Nearest-neighbour scaling keeps the supplied lightly pixelated edges.
        return pygame.transform.scale(source, self.display_size).convert_alpha()

    def select(self, facing: str, moving: bool, now_ms: int) -> pygame.Surface:
        facing = facing if facing in self.DIRECTIONS else "down"
        if moving:
            return self.frames[facing][(now_ms // 105) % 4]
        if facing == "down":
            return self.idle[(now_ms // 500) % 4]
        return self.frames[facing][0]

    def draw(
        self,
        target: pygame.Surface,
        foot_position: tuple[float, float],
        facing: str,
        moving: bool,
        now_ms: int,
        *,
        alpha: int = 255,
        tint: tuple[int, int, int] | None = None,
    ) -> pygame.Rect:
        frame = self.select(facing, moving, now_ms)
        if alpha != 255 or tint is not None:
            frame = frame.copy()
            if tint is not None:
                overlay = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
                overlay.fill((*tint, 0))
                frame.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            frame.set_alpha(alpha)
        rect = frame.get_rect(
            topleft=(
                round(foot_position[0] - self.anchor[0]),
                round(foot_position[1] - self.anchor[1]),
            )
        )
        target.blit(frame, rect)
        return rect


class CatMotion:
    """Presentation-only interpolation; logical grid coordinates stay authoritative."""

    def __init__(self, duration_ms: int = 150) -> None:
        self.duration_ms = duration_ms
        self.facing = "down"
        self.start_px = (0.0, 0.0)
        self.target_px = (0.0, 0.0)
        self.started_ms = 0
        self.moving = False

    def reset(self, position: tuple[float, float], facing: str | None = None) -> None:
        point = (float(position[0]), float(position[1]))
        self.start_px = point
        self.target_px = point
        self.started_ms = pygame.time.get_ticks()
        self.moving = False
        if facing is not None:
            self.facing = facing

    def position(self, now_ms: int | None = None) -> tuple[float, float]:
        now_ms = pygame.time.get_ticks() if now_ms is None else now_ms
        if not self.moving:
            return self.target_px
        progress = min(1.0, max(0.0, (now_ms - self.started_ms) / self.duration_ms))
        # Smoothstep removes the mechanical start/stop of a pure linear slide.
        eased = progress * progress * (3.0 - 2.0 * progress)
        point = (
            self.start_px[0] + (self.target_px[0] - self.start_px[0]) * eased,
            self.start_px[1] + (self.target_px[1] - self.start_px[1]) * eased,
        )
        if progress >= 1.0:
            self.moving = False
            self.start_px = self.target_px
        return point

    def start_move(self, destination: tuple[float, float], facing: str) -> None:
        now_ms = pygame.time.get_ticks()
        self.start_px = self.position(now_ms)
        self.target_px = (float(destination[0]), float(destination[1]))
        self.started_ms = now_ms
        self.facing = facing
        self.moving = True


class WorldTransition:
    """A cached old-frame crossfade plus one restrained expanding ring."""

    def __init__(self, size: tuple[int, int], duration_ms: int = 520) -> None:
        self.duration_ms = duration_ms
        self.effect = pygame.Surface(size, pygame.SRCALPHA)
        self.old_frame: pygame.Surface | None = None
        self.started_ms = 0
        self.center = (0, 0)
        self.from_world = 0
        self.to_world = 1

    def start(
        self,
        old_frame: pygame.Surface,
        center: tuple[int, int],
        from_world: int,
        to_world: int,
    ) -> None:
        self.old_frame = old_frame.copy()
        self.old_frame.set_alpha(255)
        self.started_ms = pygame.time.get_ticks()
        self.center = center
        self.from_world = from_world
        self.to_world = to_world

    def cancel(self) -> None:
        self.old_frame = None

    def is_active(self, now_ms: int | None = None) -> bool:
        if self.old_frame is None:
            return False
        now_ms = pygame.time.get_ticks() if now_ms is None else now_ms
        if now_ms - self.started_ms >= self.duration_ms:
            self.old_frame = None
            return False
        return True

    def draw(self, target: pygame.Surface, now_ms: int | None = None) -> None:
        if self.old_frame is None:
            return
        now_ms = pygame.time.get_ticks() if now_ms is None else now_ms
        progress = min(1.0, max(0.0, (now_ms - self.started_ms) / self.duration_ms))
        eased = progress * progress * (3.0 - 2.0 * progress)
        self.old_frame.set_alpha(round(255 * (1.0 - eased)))
        target.blit(self.old_frame, (0, 0))

        self.effect.fill((0, 0, 0, 0))
        accent = (104, 215, 243) if self.to_world == 0 else (247, 132, 176)
        radius = round(24 + 112 * eased)
        ring_alpha = round(115 * (1.0 - progress))
        pygame.draw.circle(self.effect, (*accent, ring_alpha), self.center, radius, 2)
        target.blit(self.effect, (0, 0))
        if progress >= 1.0:
            self.old_frame = None
