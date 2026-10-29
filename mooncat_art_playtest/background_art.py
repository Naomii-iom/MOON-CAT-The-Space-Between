"""Cached background-only rendering for the Guided v1.0 art playtest.

No puzzle state, input, save code, characters, tiles, or UI lives here.
"""
from pathlib import Path

import pygame


class MoonlightBackdrop:
    """Prepare the opaque scene and alpha-masked board inset once at startup."""

    def __init__(self, image_path: Path, size: tuple[int, int], board_rect: pygame.Rect):
        if not image_path.is_file():
            raise FileNotFoundError(
                f"Moonlight background PNG is missing: {image_path}. "
                "Keep main.py, background_art.py and assets/ together."
            )
        source = pygame.image.load(str(image_path)).convert_alpha()
        self.source_size = source.get_size()
        # This scene is intentionally opaque. Convert after scaling so SDL's
        # interpolated alpha cannot leave the full-screen layer at alpha 254.
        self.scene = pygame.transform.smoothscale(source, size).convert()
        self.board_rect = board_rect.copy()

        # Retain a little paper grain below the game board. A dark wash prevents
        # the forest/texture from competing with tiles and the original outlines.
        self.board = self.scene.subsurface(board_rect).copy().convert_alpha()
        wash = pygame.Surface(board_rect.size, pygame.SRCALPHA)
        wash.fill((10, 22, 43, 92))
        self.board.blit(wash, (0, 0))

        # Preserve the existing rounded board silhouette. This is a cached alpha
        # surface, not a generated fake transparency pattern or a foreground art.
        mask = pygame.Surface(board_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=20)
        self.board.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def draw(self, target: pygame.Surface) -> None:
        target.blit(self.scene, (0, 0))

    def draw_board(self, target: pygame.Surface) -> None:
        target.blit(self.board, self.board_rect.topleft)
