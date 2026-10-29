# MOON CAT — Meteorite Tile Playtest

这是独立的陨石地砖美术版本。基准是已经可运行的 `mooncat_visual_integration`；它没有覆盖项目根目录的 `main.py`、Guided v1.0、背景、小猫或旧存档。

## 运行

双击 `RUN_MOON_CAT_METEORITE_TILES.command`，或在终端运行：

```bash
cd "/Users/liuyuchen/Desktop/POLYU/mooncat/mooncat_meteorite_tiles" && ../.venv/bin/python main.py
```

## 操作

- `WASD` / 方向键：移动
- `Q`：切换世界并留下 Echo
- `H`：渐进提示
- `Z` / Backspace：撤销
- `R`：重开本关
- `G`：打开/关闭教程
- `E`：第四关灯的交互（Guided v1.0 原规则）

## 本版只改了什么

- 用用户提供的陨石 Sprite Sheet 替换主地图的程序化方形地砖。
- 裁切 Normal A/B/C/D、Special、Goal 六种形态；每种都有月光和暗影配色。
- 普通 A 在实际五关普通地面中占 78.99%，其余形态提供克制变化。
- 形态由关卡号与固定坐标决定；移动、撤销、重开、Q 切换都不会重新随机。
- 同一普通地砖在两个世界使用完全一致的 Alpha 轮廓，只改变配色。
- 特殊机关继续叠加原有标识；出口继续叠加原有动画。
- 另一世界的道路只显示低透明度陨石轮廓，不会看起来像实体平台。
- 12 张运行时地砖在初始化时加载、缩放、缓存一次。
- 整条道路以 3.4 秒周期做 ±1.5 px 正弦漂浮；每四步为一个相位组，相邻组只有 0.16 弧度的细微差异。
- 小猫、出口、机关、Echo、桥和提示环使用所在格的同一偏移；Q 切换使用绝对时间，不会重置动画。
- `main.py` 顶部的 `FLOAT_TILES_ENABLED`、`FLOAT_TILES_AMPLITUDE`、`FLOAT_TILES_PERIOD_SECONDS` 可关闭或调整动画。

没有修改背景、小猫、顶部 UI、右栏、底部说明、地图、碰撞、关卡、按键、机制或存档函数。

## 主要文件

- `assets/tiles/meteorites/original_sheet.png`：用户提供的原始图
- `assets/tiles/meteorites/moonlight/*.png`：6 张月光透明 PNG
- `assets/tiles/meteorites/shadow/*.png`：6 张暗影透明 PNG
- `assets/tiles/meteorites/tile_variants_preview.png`：两套形态对照
- `assets/tiles/meteorites/selection_manifest.json`：裁切区域和处理记录
- `tile_art.py`：只负责贴图缓存、固定分配与绘制
- `tools/prepare_meteorite_tiles.py`：可复现的素材处理脚本
- `tools/check_meteorite_tiles.py`：逻辑与渲染回归检查

## 截图与验证

- `screenshots/browser_moonlight.png`：真实 Pygbag 浏览器月光截图
- `screenshots/browser_shadow.png`：真实 Pygbag 浏览器暗影截图
- `screenshots/meteorite_layout_zoom.png`：真实 Pygame 地图区局部放大
- `screenshots/floating_idle_walk_q.gif`：真实 Pygame 的静止、行走和 Q 切换漂浮录制
- `screenshots/floating_sequence_contact_sheet.png`：GIF 关键帧检查表
- `screenshots/verification.json`：自动检查结果
- `screenshots/browser_test_result.json`：浏览器按键与控制台检查

自动检查包括：五关可解、保护逻辑 AST 一致、两世界轮廓一致、透明通道、背景与小猫文件未变、34 张运行时 PNG 只在启动加载、180 帧无重复读盘、漂浮周期连续、相邻道路最大高度差 1 px、Q 相位连续和关闭开关有效。

## 恢复

运行 Guided v1.0：

```bash
cd "/Users/liuyuchen/Desktop/POLYU/mooncat" && .venv/bin/python backups/MOON_CAT_Guided_v1.py
```

恢复本次修改前的完整视觉版本：

`backups/MOON_CAT_Visual_Integration_Pre_Meteorites_2026-10-27.zip`

删除或忽略本独立文件夹也不会影响原项目。

## 已知限制

- Codex 的受限 macOS 图形会话无法可靠创建原生 SDL 窗口；交互验证使用真实 Pygbag 浏览器，离屏渲染使用 pygame-ce。
- 浏览器 QA 的虚拟文件系统不等同于最终持久存档方案。
- 陨石图由用户提供；本项目只记录来源和处理，不推断其商用授权。公开发布前仍需由权利人确认。
