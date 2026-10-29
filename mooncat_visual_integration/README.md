# MOON CAT — Visual Integration Playtest

这是以 `backups/MOON_CAT_Guided_v1.py` 为逻辑基准制作的独立美术集成版本。它不会覆盖原项目的 `main.py`、Guided v1.0 备份或旧存档。

## 运行

双击 `RUN_MOON_CAT_VISUAL.command`，或在终端运行：

```bash
cd "/Users/liuyuchen/Desktop/POLYU/mooncat/mooncat_visual_integration" && ../.venv/bin/python main.py
```

实际项目现在位于 `/Users/liuyuchen/Desktop/POLYU/mooncat/`；文档中旧的 `/Users/liuyuchen/Desktop/香港课程/mooncat/` 已不存在。

## 操作

- `WASD` / 方向键：移动
- `Q`：切换世界并留下 Echo
- `H`：渐进提示
- `Z` / Backspace：撤销
- `R`：重开本关
- `G`：打开/关闭教程
- `E`：第四关灯的交互（保留 Guided v1.0 原规则）

## 这版改变了什么

- 月光世界使用用户提供的蓝紫色背景。
- 暗影世界使用用户提供的粉紫色背景。
- 两张背景按比例等比放大并居中裁切，不拉伸。
- 用户提供的猫咪 Sprite Sheet 被无损拆分为正面、背面、左行、右行各 4 帧，并统一脚底锚点。
- 小猫现在会按方向转身，格子间移动采用 150 ms 平滑插值；停止后保留最后朝向。
- 合法 Q 切换采用 520 ms 交叉淡化和轻微扩散光圈；期间输入暂时锁定，避免连续 Q 造成状态错误。
- 背景、20 张猫帧都只在初始化时加载一次。

地图、地砖、UI、关卡数据、碰撞、出口、Echo、H、Z、R 和存档函数保持 Guided v1.0 的原规则。

## 预览

- `screenshots/browser_moonlight.png`：月光世界，真实 Pygbag 浏览器运行截图
- `screenshots/browser_rapid_q_shadow.png`：暗影世界，真实 Pygbag 浏览器运行截图
- `screenshots/browser_q_transition.png`：Q 切换中间帧，真实 Pygbag 浏览器运行截图
- `screenshots/cat_walk_preview.gif`：真实 Pygame 渲染的连续行走预览
- `screenshots/world_transition_preview.gif`：真实 Pygame 渲染的世界切换预览

`web_preview/` 是浏览器 QA 包。需要联网加载 Pygbag 0.9.3 运行时，可在本目录执行：

```bash
python3 -m http.server 8126 --bind 127.0.0.1 --directory web_preview
```

然后打开 `http://127.0.0.1:8126/`。

## 已验证

- `main.py`、`art_assets.py` 和工具脚本通过语法检查。
- 5 个原关卡均由自动状态搜索重新验证为可解。
- `ROOMS`、`GUIDES`、`State`、`execute`、提示、存档函数与 Guided v1.0 的 AST 一致。
- 22 张运行时 PNG 启动时加载 22 次；连续渲染 180 帧后仍为 22 次，没有逐帧读盘。
- 真实浏览器操作验证四方向、合法 Q、失败 Q、快速重复 Q、H、Z、R。
- 浏览器中没有 Python Traceback。

详细结果见 `screenshots/verification.json` 与 `screenshots/browser_test_result.json`。

## 已知限制

- Codex 的受限 macOS 图形会话在 SDL 创建窗口时被系统以 `SIGABRT` 终止；因此不能把本次测试称为原生窗口实测。真实视觉与交互测试是在 Pygbag 浏览器中完成的。
- Pygbag 控制台会记录媒体需用户点击启动以及 `BrowserFS not found` 的启动提示；点击页面后游戏可正常运行，未出现 Python Traceback。
- 浏览器 QA 使用虚拟文件系统，不将其视为持久浏览器存档方案。
- 三张原始图片由用户提供；本仓库没有获得或推断第三方商用授权。发布前请由素材权利人确认许可范围。

## 回到 Guided v1.0

```bash
cd "/Users/liuyuchen/Desktop/POLYU/mooncat" && .venv/bin/python backups/MOON_CAT_Guided_v1.py
```

也可以直接忽略或删除本独立文件夹；原版没有被替换。
