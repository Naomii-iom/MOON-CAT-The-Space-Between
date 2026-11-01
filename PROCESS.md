# MOON CAT — Assignment 3 Process

## A. Initial Concept

I wanted one space to behave differently in two connected states. Moonlight and Shadow share the same coordinates, but their paths and mechanisms are different. My main design question became: “Where should I stand before I change the rules?”

I kept the input vocabulary small. Movement and the `Q` world shift carry most of the game. I wanted a simple action to create deeper decisions through consistent, visible consequences.

## B. Development and Iteration

### Core world shift

I first built grid movement and `Q` switching. A shift only succeeds when the same coordinate exists in the destination world. This keeps the visuals and collision rules consistent. Colour, paths, sound, and a short transition make each successful shift easy to notice.

### Puzzle progression

I developed the rooms as five uses of the same rule:

1. notice that the paths differ;
2. choose the right place and time to shift;
3. push a stone onto a Moonlight plate to open a Shadow route;
4. use a lantern, then place an Echo on another mechanism;
5. combine shifting and Echo placement in a final route.

I chose not to add random enemies, a boss, or unrelated collectibles. I wanted to see how much puzzle depth I could get from a small set of mechanics.

### Visuals and feedback

I moved from simple blocks to cached meteorite tiles, animated cat sprites, two landscape backgrounds, and subtle floating motion. I later removed the split information panel and boxed play area, enlarged the map and cat, darkened the background, and made solid tiles clearer. I changed other-world tiles into low-opacity outlines so they would not look walkable.

I also added clear responses for movement, failed movement, shifting, pushing, mechanisms, hints, undo, and completion. Contextual hints fade over the scene, while `G` keeps the full guide available.

## C. Real User Testing

I asked one person to play the game. My playtester said:

> “The player was unsure what the stone was for.”

The stone was visible, but its connection to the plate and the route in the other world was unclear. This showed me that seeing an object is not the same as understanding its purpose.

## D. Improvements Based on Feedback

### Stone comprehension

I kept Room 3's map and rules unchanged. I improved the way the existing relationship is communicated:

- I replaced the pushable object with a distinct transparent pixel-style stone;
- I centred it clearly inside one grid tile;
- I made the guide and progressive hints explain where to stand and push;
- I highlighted the target in the guide;
- I kept clear inactive and active plate states;
- I added particles and a message when the Shadow bridge appears;
- I added specific feedback for wrong push directions and a stone locked on the plate.

These changes clarify the stone without changing the solution.

### Strategic constraint: Echo lifetime

I also added a planning constraint, but it is separate from the stone improvement. The submitted game does **not** enforce a global move cap for a whole room. `State.moves` records successful actions, but it does not end the level.

Pressing `Q` leaves an Echo in the previous world with ten remaining successful moves. Each later move reduces the counter. The HUD shows the real value, such as `ECHO 07 / 10`. At zero, the Echo disappears. If it was holding a plate, that effect ends and the related gate can close.

I added this limit so the player must plan the route after placing an Echo instead of wandering forever. Reaching zero is not a game-over. The player can undo, restart, or create another Echo.

## E. AI Tools and Design Decisions

I used ChatGPT for discussion, design reflection, and help expressing the interaction clearly. I used OpenAI Codex / Work to assist with Python editing, debugging, asset integration, regression checks, browser experiments, screenshots, documentation, and GitHub work.

I accepted the suggestion to keep world shifting as the core interaction and build cross-world mechanisms around it. I modified or rejected suggestions for dense dashboards, large information panels, extra decoration, and unrelated mechanics. I preferred a simpler layout where the map, cat, mechanisms, Echo HUD, and other-world preview carry the important information.

I did not treat AI output as a final design decision. I selected the direction and art, provided the playtest observation, reviewed playable results, requested revisions, and decided what supported my assignment goal.

## F. Reflection

I learned that clear feedback matters more than adding features. The world-shift rule became easier to understand when the routes, mechanism states, sound, motion, and messages all agreed.

The playtest revealed a problem I had stopped noticing: the Room 3 stone was visible but its purpose was unclear. That led me to improve its visual identity and feedback instead of adding another mechanic.

The Echo lifetime makes movement more deliberate. Simplifying the UI also helped me put the focus back on the relationship between the cat, the two maps, and the active mechanism.

## Verification Evidence

- I tested the command in `README.md` with the locked uv environment.
- Automated checks cover protected puzzle logic, all five solvable rooms, keyboard mappings, cached assets, floating tiles, and rendering.
- I stored real screenshots in `mooncat_meteorite_tiles/screenshots/`.
- The Git history keeps the actual sequence of public updates.
