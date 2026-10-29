# MOON CAT — Art Integration Process

## 1. Project inspection

- Actual project: `/Users/liuyuchen/Desktop/POLYU/mooncat/`
- Engine: Python 3.14.3 + pygame-ce 2.5.8
- Stable logic baseline: `backups/MOON_CAT_Guided_v1.py`
- Resolution: 1060 × 735
- Board: 15 × 9 tiles, 44 px per tile, origin `(51, 174)`
- Movement: discrete grid actions; visual interpolation did not change logical positions
- World switch: `execute(state, "q")` remains the sole legality/collision authority
- New save path: this independent folder's `mooncat-progress.json`

## 2. Asset preparation

The three supplied images were copied unchanged into `assets/source/` before processing.

The cat sheet is a real 1983 × 793 RGBA PNG. Its black-looking empty area has alpha 0; it was not a painted black background. Nineteen character-sized connected components were detected. The first sixteen form four coherent rows:

- down/front: 4 frames
- right: 4 frames
- left: 4 frames
- up/back: 4 frames

Three later components (eyes-closed pose, paired cats and celebration pose) were deliberately excluded from locomotion. The included frames were cropped without repainting, placed on 256 × 208 transparent canvases, and aligned at a shared foot anchor `(128, 196)`. Exact source rectangles and SHA-256 hashes are in `assets/characters/cat/manifest.json`.

## 3. Background integration

Both images use a cover strategy: preserve aspect ratio, scale until the 1060 × 735 window is covered, then crop equally from left and right.

- Moonlight source 1102 × 620 → crop rectangle `(123, 0, 1060, 735)` after scaling
- Shadow source 1200 × 630 → crop rectangle `(170, 0, 1060, 735)` after scaling

The game board receives a cached translucent dark wash. This keeps the supplied atmosphere visible while preserving tile, exit and character contrast. UI cards remain opaque and are rendered last.

## 4. Cat animation

`CatSprites` loads and scales all frames once. The display canvas is 64 × 52; the visible cat is roughly one 44 px tile tall. Nearest-neighbour scaling preserves the supplied light pixel texture.

`CatMotion` interpolates only the drawn position for 150 ms. `State.player` remains the authoritative grid position. New movement input starts from the current visual position, so held movement stays continuous without changing collision rules. Walking uses about 9.5 FPS; the front idle cycle uses 2 FPS. Side/back idle keeps the last facing frame.

## 5. World transition

A legal Q action first runs the unchanged `execute()` rule. Only after success does the presentation layer start a 520 ms smooth crossfade from the last world frame to the new authoritative world. A single low-opacity ring expands from the cat. Input is ignored during this short interval, preventing repeated Q from racing state and visuals. An illegal Q uses the original message, sound and restrained shake; it does not start a full transition.

The UI is redrawn above the crossfade so labels do not double or blur.

## 6. Regression evidence

`tools/check_visual_integration.py` performs:

- protected AST comparison against Guided v1.0
- all-five-room state-space solve
- input key presence check
- sprite size/alpha validation
- startup image-load counting
- 180-frame no-reload check
- legal and illegal Q checks
- moonlight, midpoint and shadow renders

The full report is `screenshots/verification.json`.

The Pygbag browser build was then operated at the game's native 1060 × 735 viewport. Tested actions: Up, Down, Left, Right, H, Z, R, legal Q, illegal Q and two rapid Q presses. The second rapid Q was ignored during the transition and the game remained in Shadow, as intended. No Python Traceback appeared. See `screenshots/browser_test_result.json`.

Native-window launch was attempted once. The agent's restricted macOS GUI session aborted during SDL `Cocoa_RegisterApp`, before the game window was created. This is recorded as an environment limitation rather than a game pass/fail result.

## 7. AI/tool use and design decisions

- OpenAI Codex assisted with code, tests and documentation.
- The image-generation workflow was reviewed because this is an image task, but no image generator was invoked: the user's explicit instruction was to preserve the supplied assets rather than regenerate them.
- Pygame performed exact pixel crop/padding and the actual render.
- Pillow assembled preview GIFs from rendered frames.
- Pygbag 0.9.3 enabled actual browser interaction testing.

The generated paper-collage background from the earlier experiment is not used in this build.
