# MOON CAT Web Demo

This folder is the Pygbag port of my final `mooncat_meteorite_tiles` game. It keeps the five rooms, artwork, UI, maps, and puzzle rules. It does not replace the desktop version.

## Play locally

Build the Web version from the repository root:

```bash
uvx pygbag --build --archive \
  --width 1060 --height 735 \
  --title "MOON CAT — The Space Between" \
  --app_name mooncat-web-demo \
  --package io.github.naomii-iom.mooncat \
  --template mooncat_web_demo/default.tmpl \
  --icon mooncat_web_demo/favicon.png \
  mooncat_web_demo
```

Serve it through HTTP:

```bash
cd mooncat_web_demo/build/web
python3 -m http.server 8766
```

Open <http://127.0.0.1:8766/> and click once inside the game before using the keyboard.

## itch.io upload

1. Create a new itch.io project and choose **HTML** as the kind of project.
2. Upload `mooncat_web_demo/web.zip`.
3. Select **This file will be played in the browser**.
4. Use a viewport of `1060 × 735`, or enable fullscreen.
5. Save the draft and test it before publishing.

The game uses browser local storage for progress. No paid service or API is required.

## GitHub Pages

The repository deploys the prepared files in `docs/` through `.github/workflows/deploy-pages.yml`. The public URL is:

<https://naomii-iom.github.io/MOON-CAT-The-Space-Between/>
