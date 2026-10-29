"""Create a disposable async Pygbag QA copy without editing desktop main.py.

Usage: python tools/build_browser_preview.py STAGING_DIR FONT_ASSETS_DIR
"""

import ast
from pathlib import Path
import shutil
import sys


root = Path(__file__).resolve().parents[1]
stage = Path(sys.argv[1]).resolve()
font_assets = Path(sys.argv[2]).resolve()
stage.mkdir(parents=True, exist_ok=True)
source = (root / "main.py").read_text(encoding="utf-8")
tree = ast.parse(source)
loop = next(node for node in tree.body if isinstance(node, ast.While))
lines = source.splitlines(keepends=True)
prefix = "".join(lines[:loop.lineno - 1])
loop_code = "".join("    " + line for line in lines[loop.lineno - 1:loop.end_lineno])
browser_main = (
    prefix
    + "\nimport asyncio\n\nasync def browser_main():\n"
    "    global running, notice_ttl, phase_flash, shakes, mode, guide_open\n"
    "    global hint_level, hint_text, current\n"
    + loop_code
    + "\n        await asyncio.sleep(0)\n\nasyncio.run(browser_main())\n"
)
for function in ("font", "chinese_font"):
    signature = f"def {function}(size, bold=False):\n"
    browser_main = browser_main.replace(
        signature,
        signature
        + "    # Browser QA only: host system fonts are unavailable in WASM.\n"
        "    if __import__('sys').platform == 'emscripten':\n"
        "        return pygame.font.Font(str(Path(__file__).resolve().parent / 'assets' / 'NotoSansCJKsc-Regular.otf'), size)\n",
        1,
    )
compile(browser_main, str(stage / "main.py"), "exec")
(stage / "main.py").write_text(browser_main, encoding="utf-8")
shutil.copy2(root / "art_assets.py", stage / "art_assets.py")
shutil.copy2(root / "tile_art.py", stage / "tile_art.py")
shutil.copytree(root / "assets" / "backgrounds", stage / "assets" / "backgrounds", dirs_exist_ok=True)
shutil.copytree(root / "assets" / "characters", stage / "assets" / "characters", dirs_exist_ok=True)
for world in ("moonlight", "shadow"):
    shutil.copytree(
        root / "assets" / "tiles" / "meteorites" / world,
        stage / "assets" / "tiles" / "meteorites" / world,
        dirs_exist_ok=True,
    )
for name in ("NotoSansCJKsc-Regular.otf", "OFL.txt"):
    shutil.copy2(font_assets / name, stage / "assets" / name)
print(f"Browser QA source generated: {stage}")
