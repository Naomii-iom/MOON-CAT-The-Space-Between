# MOON CAT — Final Playtest Build

This folder contains my current Assignment 3 game. I kept the five puzzle maps and rules while integrating meteorite tiles, the animated cat, two backgrounds, the Room 3 stone, and the simplified full-screen UI.

## Run

```bash
uv run python mooncat_meteorite_tiles/main.py
```

## Controls

- WASD or arrow keys — move
- `Q` — shift worlds and leave an Echo
- `E` — use the Room 4 lantern
- `H` — progressive hint
- `G` — room guide
- `Z` or Backspace — undo
- `R` — restart
- Enter or Space — start or continue
- Esc — menu or quit

## Presentation

I use a 1060 × 735 window with a 15 × 9 map. The final display uses 54 px tiles and a 74 × 60 cat canvas. I darkened the backgrounds, removed the large boxed layout, and kept the route as the main visual focus. Tiles float gently as a visual effect only; collision stays on the original grid.

I load all 35 runtime PNG files once at startup: two backgrounds, twenty cat frames, twelve meteorite tiles, and one stone. Tile variants are deterministic, so they do not flicker or change after undo, restart, or a world shift.

## Verification

I checked all five rooms for solvability and tested movement, legal and illegal shifts, the Room 3 stone and plate, the Room 4 lantern, Echo expiry, undo, restart, English text, and cached asset loading. I stored real images and reports in `screenshots/`.

## Known Limits

- The Echo has a ten-move lifetime; I did not add a separate whole-level move cap.
- The current submission is a desktop pygame-ce build.
- I have not independently verified commercial rights for every supplied visual source.

My stable Guided v1.0 baseline remains at `backups/MOON_CAT_Guided_v1.py`.
