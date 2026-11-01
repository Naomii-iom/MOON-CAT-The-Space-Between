# Asset Sources and Rights Notes

## Source Files

| File | My use | Treatment |
|---|---|---|
| `assets/source/moonlight_background_original.png` | Moonlight background | Preserved source; runtime scaling and darkening |
| `assets/source/shadow_background_original.png` | Shadow background | Preserved source; runtime scaling and darkening |
| `assets/source/cat_sprite_sheet_original.png` | Cat animation | Deterministic crop, transparent padding, shared foot anchor |
| `assets/tiles/meteorites/original_sheet.png` | Meteorite tiles | Preserved source; deterministic crop, cleanup, transparent canvas, and two colour sets |
| `assets/objects/stone_source.png` | Room 3 stone | Deterministic alpha cleanup and sizing |

I did not download game art for this version or use a generative model to redraw the final meteorites or stone.

## Rights Note

I received these images through my project workflow. I recorded their source copies and technical treatment, but I cannot independently confirm authorship, exclusivity, or commercial licensing. I would confirm redistribution rights before any commercial release.

## Tools

- OpenAI Codex — integration, testing, and documentation assistance
- Pillow — deterministic cropping, alpha cleanup, transparent PNG output, and colour variants
- pygame-ce — cached runtime rendering
- Pygbag 0.9.3 — historical browser QA
