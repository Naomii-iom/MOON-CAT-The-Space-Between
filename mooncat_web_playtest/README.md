# MOON CAT — Guided v1.0 Web Playtest

这是从 `backups/MOON_CAT_Guided_v1.py` 制作的独立 Pygbag 网页试玩版。原项目的 `main.py`、`backups/` 和所有 `mooncat-*.json` 存档均未修改。

## 直接交付文件

- `MOON_CAT_Guided_v1_Web_Playtest_itch.zip`：上传到 itch.io 的 HTML5 包。
- `main.py`：Guided v1.0 的网页兼容副本。
- `assets/NotoSansCJKsc-Regular.otf`：浏览器中文字体。
- `assets/OFL.txt`：字体许可证。
- `dist/`：本地浏览器预览文件。
- `screenshots/`：真实浏览器测试截图。

## 本地预览

在终端运行：

```bash
cd "/Users/liuyuchen/Desktop/香港课程/mooncat/mooncat_web_playtest"
python3 -m http.server 8123 --bind 127.0.0.1 --directory dist
```

然后打开 <http://127.0.0.1:8123/>。第一次加载会从 Pygbag 官方 CDN 获取 Python/WebAssembly 运行时；出现绿色提示后点击页面，再按 Enter 开始。

## itch.io 上传步骤

1. 登录 itch.io，进入 Dashboard，选择 **Create new project**。
2. 填写标题；将 **Kind of project** 设为 **HTML**。
3. 在 Uploads 中上传 `MOON_CAT_Guided_v1_Web_Playtest_itch.zip`。
4. 勾选 **This file will be played in the browser**。
5. Embed options 选择手动尺寸，宽 `1060`、高 `735`；建议同时允许 Fullscreen。
6. 页面先保持 **Draft** 或 **Restricted**，保存后用 itch.io 的预览页测试：点击游戏区域，按 Enter，检查 WASD、Q、H、Z、R。
7. 确认无误后再由你自己决定是否公开。本次工作没有上传或发布任何内容。

ZIP 根目录已确认直接包含：

```text
index.html
favicon.png
mooncat_web_playtest.apk
```

## 浏览器兼容说明

- 主循环已改为 `asyncio`，每帧把控制权交回浏览器。
- 键位保持原样：WASD/方向键移动、Q 切换、E 互动、Z 撤销、H 提示、R 重开、G 教程。
- 画面逻辑尺寸保持 `1060 × 735`，浏览器会等比缩放。
- 中文使用随包的 Noto Sans CJK SC，不依赖玩家电脑字体。
- 游戏画面与音效仍由代码生成，没有遗漏的图片或音频路径。
- 浏览器进度保存在 `localStorage`，键名为 `mooncat-guided-v1-web-progress`；清除站点数据、无痕模式结束或换域名会丢失进度。
- 浏览器自动播放规则要求玩家先点击游戏区域，之后生成音效才能正常启用。

## 已完成的真实浏览器测试

- Pygbag `0.9.3` 构建和 itch.io ZIP 归档：通过。
- 页面首次加载与点击启动：通过。
- 菜单、1060×735 画面缩放、中文教程字体：通过。
- WASD、Q、H、Z、R：通过。
- 第一关完整通关：通过。
- 第二关 Echo、跨世界开门和完整通关：通过。
- 刷新页面后保留解锁进度：通过。
- 强制走 itch.io 使用的 `.apk` 加载分支：通过。
- 游戏启动后浏览器未出现 Python 异常：通过。
- 尚未在真实 itch.io 页面上传测试，因为用户要求不要擅自发布。

## 恢复原版

网页版是独立目录，删除或忽略这个目录即可退回原版。也可以直接运行稳定备份：

```bash
cd "/Users/liuyuchen/Desktop/香港课程/mooncat"
uv run backups/MOON_CAT_Guided_v1.py
```

制作前后原版 SHA-256：

```text
backups/MOON_CAT_Guided_v1.py
ac0fa746c267118be50a35220b6d92f43c512ee78923836eda8bab939d5783e9

main.py
ba7093cb0016c0d18a30d8327707594a5f04ea8d4cc470b602dab59538890f0d
```
