# MOON CAT — Visual Integration Playtest

I kept this historical folder to show the stage where I first combined Guided v1.0 with the two supplied backgrounds and animated cat. It does not overwrite my stable baseline or final build.

## Run

```bash
uv run python mooncat_visual_integration/main.py
```

## What I Added

- cover-scaled Moonlight and Shadow backgrounds;
- four-direction cat animation from the supplied sprite sheet;
- 150 ms visual movement interpolation;
- a 520 ms world crossfade after a legal `Q`;
- startup caching for backgrounds and cat frames.

I kept the original maps, collision, exits, Echo, hints, undo, restart, and save rules.

## Controls

Use WASD or arrow keys to move, `Q` to shift, `E` for the Room 4 lantern, `H` for hints, `G` for the guide, `Z` to undo, and `R` to restart.

I stored browser screenshots, preview GIFs, and verification reports in `screenshots/`. For my current submission build, I run:

```bash
uv run python mooncat_meteorite_tiles/main.py
```
