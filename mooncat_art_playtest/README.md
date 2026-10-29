# MOON CAT 月光剪纸美术试玩 · 第一阶段

本目录是 Guided v1.0 的独立副本，仅接入月光世界背景。请先确认月光风格，再制作同构图的暗影背景。菜单和暗影世界当前保留原有绘制。

## 运行这个版本

在终端执行一条命令：

```bash
cd "/Users/liuyuchen/Desktop/POLYU/mooncat/mooncat_art_playtest" && ../.venv/bin/python main.py
```

也可以双击本目录的 `RUN_MOON_CAT_ART.command`。按 Enter 开始，第二次 Enter 关闭原有关卡指南，便能看到背景。WASD/方向键移动，Q 切换，Z 撤销，R 重开。

这是以 `backups/MOON_CAT_Guided_v1.py` 为基础的版本，不是根目录后来修改过的 `main.py`（后者有 12 步 Echo 等玩法差异）。这次没有把两个版本的玩法混合。

## 文件

- `main.py`：独立 Guided v1.0 副本；只增加背景初始化和两个背景绘制入口。
- `background_art.py`：启动时加载、缩放 PNG，缓存整屏背景与圆角棋盘底纹。
- `assets/backgrounds/moonlight_paper_v1.png`：1536×1024、不透明 RGB PNG 原图；启动时一次缩放到 1060×735。
- `assets/backgrounds/moonlight_prompt.txt`：本次 AI 生成的完整提示词。
- `screenshots/moonlight_live_browser.jpg`：真实浏览器中运行 Pygame 的截图。
- `screenshots/moonlight_offscreen_render.png`：桌面 Pygame 的 1060×735 离屏渲染，保留原有 macOS 字体；不是原生窗口截图。
- `screenshots/verification.json`、`browser_test_result.json`：测试记录。
- `PROCESS.md`：美术选择、素材来源、AI 使用与阶段记录。
- `web_preview/`：用于实际操作验证的独立 Pygbag 测试构建。

## 本次验证与限制

- 真实浏览器运行了 Pygame：进入第一关、新背景显示、W/D 移动、Q 切换至旧暗影背景、Z 回退、R 重开均成功；没有捕获到 Python Traceback。
- 桌面版在当前执行环境中无法成功注册 macOS GUI，因此本次没有宣称完成原生窗口试玩。上述本地命令供你在正常终端运行。
- AST 对比确认关卡、移动、Q/Echo、提示、存档函数、按键主循环、小猫与 UI 绘制代码与 Guided v1.0 一致。
- 固定状态/时间对比确认抽检的道路、小猫、出口、右栏和底部 UI 内部像素未改变（圆角外露的背景不属于前景对比区域）。
- 连续 180 帧仅调用了一次 PNG 读取；离屏 CPU 绘制中位数约 0.89 ms、95 分位约 1.26 ms。这不是原生窗口/浏览器帧率测量。
- 资源路径由 `__file__` 定位，运行命令不需要依赖素材目录作为当前路径。
- 本次是完整不透明背景，不需要透明装饰 PNG；内存中的圆角棋盘层保留正确 Alpha，角落为 0，内部为 255。
- 浏览器 QA 副本仅添加 async 循环与随包 Noto 字体，以便真实操作验证；没有把这些改动加入桌面 `main.py`。QA 页不是新发布版，未上传 itch.io。

## 可选浏览器预览

```bash
cd "/Users/liuyuchen/Desktop/POLYU/mooncat/mooncat_art_playtest" && python3 -m http.server 8125 --bind 127.0.0.1 --directory web_preview
```

打开 <http://127.0.0.1:8125/>，等待加载后点击页面，再按两次 Enter。该预览需要联网加载 Pygbag 运行时。其临时浏览器文件系统不作为持久进度存储；桌面版保存方式与基准完全相同。

## 存档与恢复

独立副本仍使用原 `SAVE_FILE` 和存档函数，因此它只会在**本目录**创建 `mooncat-progress.json`。没有复制已有进度，也不会写入上级目录或 `backups/`。

回到原版只需停止这个试玩版，运行上级目录原程序；或运行稳定备份：

```bash
cd "/Users/liuyuchen/Desktop/POLYU/mooncat" && .venv/bin/python backups/MOON_CAT_Guided_v1.py
```

制作前后校验一致：

```text
backups/MOON_CAT_Guided_v1.py
ac0fa746c267118be50a35220b6d92f43c512ee78923836eda8bab939d5783e9
main.py（上级目录原程序）
ba7093cb0016c0d18a30d8327707594a5f04ea8d4cc470b602dab59538890f0d
```
