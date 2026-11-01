# MOON CAT — Assignment 3 Process

## A. Initial Concept

The initial concept was to make one space behave differently in two states.
The Moonlight and Shadow worlds share a coordinate system, but their paths and
mechanisms are not identical. The central question is therefore not simply
“Where can I walk?” but “Where should I stand before I change the rules?”

The project deliberately uses a small input vocabulary. Movement and `Q` world
shifting carry most of the design. This follows the idea that a simple action
can create deeper decisions when its consequences are consistent and visible.

## B. Development and Iteration

### Core world shift

The first playable version established grid movement and `Q` switching. A
shift is only legal when the player's coordinate exists in the destination
world. This prevents the visual world state from contradicting collision.
World colour, paths, sound, and a short transition provide immediate feedback.

### Puzzle progression

The rooms were developed as a sequence of applications of the same rule:

1. observe that paths differ between worlds;
2. choose the correct location and timing for a shift;
3. push a stone onto a Moonlight pressure plate to create access in Shadow;
4. interact with a lantern, then use an Echo to hold a separate mechanism;
5. combine shifting and Echo placement in a final route.

The design avoided adding random enemies, a boss, or unrelated collectibles.
The purpose was to test whether a small number of mechanics could produce
readable puzzle decisions.

### Visual and feedback development

The project moved from programmatic blocks to cached meteorite tiles, animated
cat sprites, two landscape backgrounds, and a restrained floating motion. The
visual layout was later simplified: the large split information panel and the
boxed play area were removed, the map and cat were enlarged, the background
was darkened, and solid tiles were given clearer edges and shadows. Ghost tiles
for the other world became low-opacity outlines so they could not be mistaken
for walkable ground.

Interaction feedback was developed alongside the visuals. Legal movement,
failed movement, world shifts, pushing, mechanism activation, hints, undo, and
room completion each produce an observable response through animation, sound,
particles, colour, state change, or contextual text. Hints fade over the scene
instead of occupying a large panel, while `G` keeps the full room guide
available when needed.

## C. Real User Testing

One real user played the game. The observed feedback was:

> “The player was unsure what the stone was for and did not understand its role in the puzzle.”

The player noticed the Room 3 object but did not understand the relationship
between pushing it, the pressure plate, and the route that appears in the other
world. This exposed a comprehension problem that was not obvious from the
designer's perspective: visibility of an object does not automatically explain
its function.

## D. Improvements Based on Feedback

### Stone comprehension

The implemented improvements did not change Room 3's coordinates or rules.
They improved how the existing dependency is communicated:

- the pushable object was replaced with a distinct, transparent pixel-style
  stone sprite centred inside its grid tile;
- the room guide and progressive hints explicitly direct the player to stand
  to the stone's left and push it toward the pressure plate;
- the guide marker highlights the relevant target;
- the pressure plate has inactive and active visual states;
- reaching the plate produces particles and a contextual message explaining
  that the Shadow bridge has appeared;
- incorrect pushing directions and the locked-on-plate state return specific
  feedback instead of failing silently.

These changes address the stone's purpose directly without adding a new tool or
changing the puzzle solution.

### Move constraint: Echo lifetime

Code review confirmed that the implemented constraint is **not a global move
limit for an entire room**. `State.moves` records successful actions, but no
whole-level cap is enforced. The actual decision-making constraint is the
Echo's ten-move lifetime, which is separate from the stone clarification work.

Pressing `Q` leaves an Echo at the player's coordinate in the departed world
with ten remaining player moves. Each subsequent successful movement action
reduces that number. The top HUD displays the actual state as, for example,
`ECHO 07 / 10`. This encourages the player to plan the route from the Echo-held
plate to the door instead of wandering indefinitely while the mechanism stays
active.

When the count reaches zero, the Echo is removed. If it was holding a pressure
plate, that mechanism is no longer active and the related gate can close. The
player does not receive a separate game-over; they may undo, restart, or create
another Echo. This is the behaviour present in the submitted code and is not
described as a whole-level failure system.

## E. AI Tools and Design Decisions

ChatGPT was used for discussion, design reflection, and drafting clearer ways
to describe the interaction. OpenAI Codex / Work was used to inspect and edit
the Python project, integrate supplied assets, debug pygame and Pygbag issues,
write regression checks, capture real rendered evidence, and prepare the Git
repository and documentation.

**Accepted suggestion:** the project retained world switching as its core
interaction and developed cross-world mechanisms and feedback around it.

**Modified / rejected suggestion:** proposals for dense dashboards, large
information panels, extra decorative systems, and more complicated mechanics
were rejected or simplified. The final direction removed the split UI and
large boxed map so that the playable route, cat, mechanisms, compact Echo HUD,
and other-world preview carry the information.

AI output was not treated as an automatic design decision. Liu Yuchen selected
the game direction and art, provided the real-user observation, evaluated the
playable results, requested revisions, and decided which suggestions supported
the assignment goal. Asset-processing records distinguish deterministic image
cleanup from generative work.

## F. Reflection

The project showed that clear interaction feedback is more valuable than
adding more features. The world-shift rule became easier to understand when
routes, mechanism states, sound, motion, and concise messages agreed with one
another.

Real user testing revealed an interpretation problem that the designer had
stopped noticing: the Room 3 stone was visible but its purpose was not clear.
That observation led to targeted visual and feedback changes rather than a new
mechanic.

The Echo lifetime adds a planning constraint by making the player consider how
many moves remain while an Echo holds a mechanism. Finally, simplifying the UI
made the most important interaction—the relationship between the player, the
two maps, and the active mechanism—more prominent.

## Verification Evidence

- The final local command is documented in `README.md` and tested with the
  locked uv environment.
- Automated checks verify protected puzzle/state functions, all five solvable
  rooms, keyboard mappings, cached asset loading, floating-tile continuity,
  and rendering.
- Real screenshots are stored in `mooncat_meteorite_tiles/screenshots/`.
- Git history preserves the actual sequence of public submission updates.
