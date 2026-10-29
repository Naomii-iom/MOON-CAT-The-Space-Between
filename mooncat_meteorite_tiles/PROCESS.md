# MOON CAT — Meteorite Tile Integration Process

## 1. 锁定基准

- 实际项目：`/Users/liuyuchen/Desktop/POLYU/mooncat/`
- 修改基准：`mooncat_visual_integration`
- 稳定逻辑基准：`backups/MOON_CAT_Guided_v1.py`
- 分辨率：1060 × 735
- 地图：15 × 9，地砖 44 px，原点 `(51, 174)`
- 小猫显示画布：64 × 52
- 改动前备份：`backups/MOON_CAT_Visual_Integration_Pre_Meteorites_2026-10-27.zip`

原版本、Guided v1.0 与根目录存档均未覆盖。

## 2. 素材处理

原图 1774 × 887 RGBA，并不是统一网格。脚本先按真实不透明连通区域测量，选择六个质量稳定的形态，再进行：

1. 在每个测量矩形外保留 10 px 安全边缘；
2. 删除电光洋红/蓝色杂边；
3. 只保留最大主体及 3 px 抗锯齿边缘；
4. 裁至真实 Alpha 边界；
5. 等比缩放并居中到 64 × 64 透明画布；
6. 依据原图明度映射灰蓝与灰紫/褪粉两套色阶。

没有生成、补画或锐化石头。`source_cutouts/` 保留清理后的中性源形态；精确裁切矩形和调色板位于 `selection_manifest.json`。

## 3. 运行时集成

`MeteoriteTiles` 在初始化时读取月光/暗影各 6 张 PNG，并一次性缩放到 44 × 44。贴图种类由 `room_index`、`x`、`y` 的固定公式决定，普通 A/B/C/D 目标比例为 75/10/10/5。实际五关普通地面统计为 94/9/10/6，Normal A 占 78.99%。

出口只在它所属世界使用 Goal 底砖；踏板、门与灯使用 Special 底砖，所有原有交互图标继续画在上层。另一世界道路使用预先缓存的低透明度蒙版和轮廓。碰撞仍完全由 `State.floor()` 和 `execute()` 决定。

漂浮是纯绘制偏移：默认幅度 ±1.5 px，周期 3.4 秒，使用 `pygame.time.get_ticks()` 驱动正弦波。两个世界地面取并集后做 BFS，每四格距离共享一个相位，相邻组只差 0.16 弧度；所以道路整体呼吸，但不会像独立方块一样互相错开。相位只由关卡与坐标决定，不读取当前世界，因此 Q 过渡前后连续。地砖下方使用缓存的 28 Alpha 椭圆阴影。

`visual_tile_center()` 只用于绘制机关、出口、桥、Echo、记忆、提示环和角色；`tile_center()`、`State.player`、碰撞和移动仍使用原逻辑坐标。三个常量可直接调节或关闭：`FLOAT_TILES_ENABLED`、`FLOAT_TILES_AMPLITUDE`、`FLOAT_TILES_PERIOD_SECONDS`。

## 4. 验证

`tools/check_meteorite_tiles.py` 已执行：

- `ROOMS`、`GUIDES`、`State`、`execute`、提示、存档函数与修改前基准 AST 一致；
- 五关状态空间搜索全部找到解；
- 背景和 20 张小猫 PNG 与修改前基准逐文件 SHA-256 一致；
- 12 张地砖均为 64 × 64 RGBA，透明范围 0–255；
- 相同形态的两世界 Alpha 字节完全一致；
- 启动加载 34 张 PNG，连续 180 帧后仍为 34 次；
- 合法/非法 Q 与世界切换渲染通过；
- 漂浮采样未超过 ±2 个整数像素，相邻道路最大差 1 px；完整周期首尾一致；Q 前后同坐标相位一致；关闭测试归零；
- 离屏 180 帧中位绘制约 0.59 ms（只作回归参考，不代表浏览器 FPS）。

浏览器验证另记于 `screenshots/browser_test_result.json`。真实浏览器截图不得替代或伪装成概念图。

## 5. AI 与工具记录

- OpenAI Codex 协助代码、验证和文档。
- 已阅读图像处理工作流；因为用户要求严格保留原陨石造型，没有调用图像生成模型。
- Pillow 仅执行确定性的裁切、Alpha 清理、统一画布、调色与预览排版。
- pygame-ce 执行真实游戏渲染；Pygbag 0.9.3 用于浏览器交互测试。
