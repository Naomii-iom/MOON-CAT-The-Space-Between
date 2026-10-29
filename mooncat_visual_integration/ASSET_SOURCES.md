# Asset Sources and Rights Notes

## User-provided source files

| Source copy | Role | Technical treatment |
|---|---|---|
| `assets/source/moonlight_background_original.png` | Moonlight World background | Exact copy; runtime cover-scale and centered crop only |
| `assets/source/shadow_background_original.png` | Shadow World background | Exact copy; runtime cover-scale and centered crop only |
| `assets/source/cat_sprite_sheet_original.png` | Cat animation source | Exact copy; deterministic crop, transparent padding and shared foot anchor |

The source files were supplied by the user in this conversation as the approved visual direction. No online game assets were downloaded or copied for this build.

The game-ready background files in `assets/backgrounds/` are byte-for-byte copies of the supplied backgrounds. The frames in `assets/characters/cat/` retain the supplied pixels and alpha; they were not repainted or regenerated.

## Rights status

The integration records provenance but cannot independently verify authorship, exclusivity, or commercial licensing of user-supplied files. Before public or commercial distribution, the user/rightsholder should confirm that all three source images may be redistributed in the game.

## AI and tooling disclosure

- Integration code and documentation were assisted by OpenAI Codex.
- No image-generation model was used to redraw these three assets in this version.
- Pygame performed deterministic sprite extraction and runtime rendering.
- Pillow assembled GIF previews from frames rendered by the actual Pygame build.
- Pygbag 0.9.3 provided the browser QA runtime.
