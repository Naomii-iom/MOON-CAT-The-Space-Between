# MOON CAT — The Space Between

**SD5913 Assignment 3 — Interaction Design Prototype**

I made MOON CAT as a short puzzle game in Python and pygame-ce. I explore one space in two connected states: Moonlight and Shadow. Pressing `Q` changes the active world, so paths, bridges, doors, and mechanisms can change too.

My final submission version is in [`mooncat_meteorite_tiles/`](mooncat_meteorite_tiles/).

![MOON CAT gameplay](mooncat_meteorite_tiles/screenshots/level1_english_ui.png)

## Project Overview

I built five compact puzzle rooms around one main idea. Instead of adding many unrelated controls, I ask the player to compare both worlds, choose where to move, and shift at the right location. Later rooms add a pushable stone, a pressure plate, a lantern, bridges, doors, and a temporary Echo.

## Intended Users

I designed the game for people who enjoy exploration and light puzzle solving. I kept the controls small and included progressive hints, undo, and restart so experimentation does not feel punishing.

## Core Interaction

The player moves on a grid and presses `Q` to shift between Moonlight and Shadow. Both worlds use the same coordinates, but their walkable routes and mechanisms differ. A room is solved by understanding how an action in one world changes access or state in the other.

## Input → Response → Feedback

I implemented this loop in `mooncat_meteorite_tiles/main.py`:

| Input | System response | Visible feedback |
|---|---|---|
| `WASD` / arrow key | Checks the destination and moves the cat or pushes the Room 3 stone | Cat animation, sound, and tile alignment; a failed move gives a shake, sound, and short message |
| `Q` | Checks the matching coordinate, switches world, and leaves an Echo behind | World crossfade, colour change, new roads, Echo sprite, sound, and updated HUD |
| `E` | Uses the Room 4 lantern from the correct position and world | Lantern and bridge changes, particles, sound, and a short message |
| Stone reaches plate | Activates the cross-world bridge | Active plate art, particles, and a message that the Shadow bridge is available |
| Echo expires | Removes the Echo after ten successful moves | The `ECHO 07 / 10` counter decreases; at zero, the Echo and its plate effect disappear |
| `H`, `G`, `Z`, `R` | Shows help, opens the guide, undoes, or restarts | Progressive hints, a guide overlay, restored state, or a room reset |

I use map changes, animation, sound, colour, the HUD, and short contextual text so the result of an action is easy to notice.

## Controls

- `W`, `A`, `S`, `D` or arrow keys — move
- `Q` — shift worlds and leave an Echo
- `E` — use the Room 4 lantern
- `H` — show a progressive hint
- `G` — open or close the room guide
- `Z` or Backspace — undo one action
- `R` — restart the current room
- Enter or Space — start, close the guide, or continue
- `1`–`5` — select an unlocked room
- Esc — return to the menu; press again to quit

## Installation and Running

### Requirements

- macOS, Windows, or Linux with keyboard input
- [uv](https://docs.astral.sh/uv/)
- Git

```bash
git clone https://github.com/Naomii-iom/MOON-CAT-The-Space-Between.git
cd MOON-CAT-The-Space-Between
uv sync --frozen
uv run python mooncat_meteorite_tiles/main.py
```

`uv` reads `.python-version`, creates a local environment, and installs the locked `pygame-ce` dependency from `uv.lock`.

## Screenshots

### Full-screen puzzle view

![Full-screen puzzle view](mooncat_meteorite_tiles/screenshots/level1_english_ui.png)

### Room 3 pushable stone

![Room 3 stone](mooncat_meteorite_tiles/screenshots/level3_english_ui.png)

### Echo remaining-move HUD

![Echo HUD](mooncat_meteorite_tiles/screenshots/fullscreen_ui_echo_hud.png)

## Evidence and Documentation

- [`PROCESS.md`](PROCESS.md) — my concept, iteration, real playtest, decisions, and reflection
- [`CREDITS.md`](CREDITS.md) — authorship, tools, assets, licences, and AI disclosure
- [`verification.json`](mooncat_meteorite_tiles/screenshots/verification.json) — automated regression evidence
- [`browser_test_result.json`](mooncat_meteorite_tiles/screenshots/browser_test_result.json) — browser test record

## Known Limitations

- I implemented a ten-move lifetime for each Echo, not a separate limit for the whole level. At zero, the Echo and its mechanism effect disappear; the room does not end.
- I verified the latest submission as a desktop pygame-ce project. An older Pygbag experiment remains in the repository, but I do not currently have a hosted live demo.
- I received the visual source files through my project workflow. I have not independently verified commercial redistribution rights, so I present this repository as coursework.

## Credits and AI Usage

I made the concept and interaction decisions, selected the art direction, ran the playtest, and chose the revisions. I used ChatGPT for early discussion and design reflection. I used OpenAI Codex / Work to help with programming, debugging, automated checks, asset integration, documentation, and GitHub preparation. I reviewed every suggestion and accepted, changed, or rejected it based on playtesting and my goal of keeping the map readable.

I recorded the full details in [`CREDITS.md`](CREDITS.md) and [`PROCESS.md`](PROCESS.md).
