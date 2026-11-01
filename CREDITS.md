# MOON CAT — Credits and AI Disclosure

## Student Role

**Liu Yuchen** — concept direction, game-design decisions, puzzle evaluation,
art selection and direction, real-user testing, iteration decisions, and final
submission review.

## Software and Libraries

- Python
- [pygame-ce](https://pyga.me/) — desktop game runtime and rendering
- [uv](https://docs.astral.sh/uv/) — Python version, dependency, and lockfile management
- [Pygbag](https://pygame-web.github.io/) — experimental browser-build testing
- Pillow — deterministic asset cropping, alpha cleanup, recolouring, and preview generation
- Git and GitHub — version control and public submission repository

## Visual Assets

The final project uses source images supplied through the student's project
workflow:

- Moonlight landscape background
- Shadow landscape background
- Cat sprite sheet
- Meteorite tile sprite sheet
- Room 3 pushable-stone image

The repository preserves source/processed files and technical notes in
`mooncat_meteorite_tiles/assets/`, `ASSET_SOURCES.md`, and `PROCESS.md` inside
the final-version folder. Processing included deterministic cropping,
transparent-alpha cleanup, sizing, colour mapping, and runtime integration.
The supplied stone was not regenerated.

The web-playtest folder includes Noto Sans CJK SC under the SIL Open Font
License; its `OFL.txt` is included beside the font.

No claim is made that the project independently verified commercial
redistribution rights for every supplied visual source. This public repository
is submitted as coursework; further publication should include a separate
rights review.

## AI Tools

### ChatGPT

Used for design discussion, puzzle and usability reflection, planning, and
drafting documentation. Suggestions were reviewed rather than accepted
automatically.

### OpenAI Codex / Work

Used for Python/pygame implementation assistance, debugging, asset integration,
test automation, browser-build investigation, screenshot capture, Git/GitHub
operations, and final documentation preparation.

### AI and image decisions

AI-assisted visual exploration occurred during the broader project workflow.
For the submitted meteorite tiles and the final Room 3 stone replacement,
Codex used the supplied images and deterministic processing rather than
generating replacement artwork. The student selected the visual direction and
approved or rejected changes based on readability and playtesting.

## Design Responsibility

The student retained responsibility for the submitted design. In particular:

- the dual-world mechanism was accepted and developed as the core interaction;
- dense UI panels and excessive decoration were rejected or simplified;
- the map was prioritised as the main visual focus;
- real-user feedback about the stone was selected as the key usability issue;
- final art choices and revision requests were made by the student.
