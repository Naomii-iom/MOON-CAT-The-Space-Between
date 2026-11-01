# MOON CAT — Guided v1.0 Web Playtest

I made this independent Pygbag build from Guided v1.0 to test browser compatibility. I kept the original desktop files, backups, and saves unchanged. This is a historical experiment, not my current submission build.

## Included Files

- `MOON_CAT_Guided_v1_Web_Playtest_itch.zip` — HTML5 upload package
- `main.py` — browser-compatible Guided v1.0 copy
- `assets/NotoSansCJKsc-Regular.otf` and `assets/OFL.txt` — bundled font and licence
- `dist/` — local browser preview
- `screenshots/` — real browser evidence

## Local Preview

```bash
python3 -m http.server 8123 --bind 127.0.0.1 --directory mooncat_web_playtest/dist
```

Open <http://127.0.0.1:8123/>, wait for loading, click the game, and press Enter.

## itch.io Test Upload

1. Create an HTML project in the itch.io dashboard.
2. Upload `MOON_CAT_Guided_v1_Web_Playtest_itch.zip`.
3. Mark the file as playable in the browser.
4. Use a 1060 × 735 embed and allow fullscreen.
5. Keep the page Draft or Restricted while testing.
6. Check Enter, movement, `Q`, `H`, `Z`, and `R` before publishing.

I did not publish this build. The archive contains `index.html`, `favicon.png`, and `mooncat_web_playtest.apk` at its root.

## Browser Notes

I changed the copied loop to `asyncio` so it yields once per frame. The logical size stays 1060 × 735. The bundled font avoids depending on a local system font. Browser progress uses `localStorage` with the key `mooncat-guided-v1-web-progress`, so clearing site data removes progress.

I tested startup, scaling, input, the first two rooms, refresh persistence, and the packaged `.apk` path in a real browser without a Python exception. I did not test this archive on a real itch.io page because I did not want to publish without approval.

For the current desktop game, I run:

```bash
uv run python mooncat_meteorite_tiles/main.py
```
