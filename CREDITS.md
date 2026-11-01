# MOON CAT — Credits and AI Disclosure

## My Role

I am Liu Yuchen. I made the concept, chose the game-design direction, evaluated the puzzles, selected the art direction, organised the playtest, and decided on the final revisions.

## Software and Libraries

- Python
- [pygame-ce](https://pyga.me/) — game runtime and rendering
- [uv](https://docs.astral.sh/uv/) — Python and dependency management
- [Pygbag](https://pygame-web.github.io/) — experimental browser testing
- Pillow — deterministic cropping, alpha cleanup, recolouring, and previews
- Git and GitHub — version control and public submission

## Visual Assets

I used visual source files collected through my project workflow:

- Moonlight landscape background
- Shadow landscape background
- Cat sprite sheet
- Meteorite tile sprite sheet
- Room 3 pushable-stone image

I kept the source and processed files with technical notes in the version folders. Processing included deterministic cropping, transparent-alpha cleanup, sizing, colour mapping, and integration. I did not regenerate the final stone.

The web experiment includes Noto Sans CJK SC under the SIL Open Font License. I included its original `OFL.txt`.

I have not independently confirmed commercial redistribution rights for every visual source. I am sharing this repository as coursework, and I would complete a separate rights review before wider publication.

## AI Tools

### ChatGPT

I used ChatGPT for design discussion, puzzle and usability reflection, planning, and help drafting documentation. I reviewed its suggestions instead of accepting them automatically.

### OpenAI Codex / Work

I used Codex / Work to assist with Python and pygame development, debugging, asset integration, automated checks, browser-build investigation, screenshot capture, GitHub work, and documentation.

### My decisions

I accepted the dual-world mechanism as the core interaction and developed clearer puzzle feedback around it. I changed or rejected suggestions for dense UI panels, excessive decoration, and extra mechanics. I chose to make the map the visual focus. I also chose the Room 3 stone issue as the main usability finding after the playtest.

AI-assisted visual exploration happened earlier in the project. For the submitted meteorite tiles and final Room 3 stone, I used the supplied images with deterministic processing instead of generating replacement artwork.
