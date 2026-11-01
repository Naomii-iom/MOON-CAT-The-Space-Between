# MOON CAT — Moonlight Art Playtest

I kept this folder as my first background-art experiment based on Guided v1.0. It adds the Moonlight paper-collage background while leaving the Shadow background and game rules unchanged. It is not my final submission build.

## Run

```bash
uv run python mooncat_art_playtest/main.py
```

Press Enter to start and Enter again to close the guide. Use WASD or arrow keys to move, `Q` to shift, `Z` to undo, and `R` to restart.

## What I changed

- I loaded and cached one Moonlight background at startup.
- I kept the Guided v1.0 maps, movement, shifting, Echo, hints, saves, cat, and UI rules.
- I stored browser and off-screen evidence in `screenshots/`.
- I kept the AI image prompt in `assets/backgrounds/moonlight_prompt.txt`.

## Notes

I verified this historical experiment in a Pygbag browser build. Its browser file system is not a final save solution, and I did not publish it to itch.io. For the current game, I run:

```bash
uv run python mooncat_meteorite_tiles/main.py
```
