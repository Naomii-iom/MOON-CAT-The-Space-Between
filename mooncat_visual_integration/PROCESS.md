# MOON CAT — Visual Integration Process

## Inspection and Preparation

I used Guided v1.0 as the stable logic reference. The game runs at 1060 × 735 with a 15 × 9 logical board. I copied the three supplied source images unchanged before processing them.

I found sixteen coherent locomotion frames in the cat sheet: four each for front, right, left, and back. I excluded the later special poses from walking. I cropped the frames without repainting and aligned them to one foot anchor.

## Backgrounds and Cat

I cover-scaled both backgrounds to the window and cropped them from the centre without stretching. I added a restrained dark wash behind the board for readability.

I cached all cat frames at startup. I interpolated only the drawn position for 150 ms, while the original grid state stayed authoritative. A legal `Q` first passes the unchanged rule, then starts a short crossfade. I ignore extra input during that transition so state and visuals cannot race.

## Verification

I compared protected logic with Guided v1.0, solved all five rooms with state-space checks, counted image loads, rendered 180 frames without repeated disk reads, and tested legal and illegal world shifts. I also tested the Pygbag QA build with keyboard input and found no Python traceback.

My restricted macOS GUI session could not create a native SDL window during this historical test, so I recorded that as an environment limit instead of claiming a desktop pass.

## AI and Tools

I used Codex to assist with code, tests, and documentation. I did not use an image generator for these three supplied assets because I wanted to preserve them. Pygame handled extraction and rendering, Pillow assembled preview GIFs, and Pygbag supported browser QA.
