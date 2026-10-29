# Asset Sources and Rights Notes

## 用户提供的源文件

| 文件 | 用途 | 本版处理 |
|---|---|---|
| `assets/source/moonlight_background_original.png` | 月光背景 | 沿用上一版，字节未改 |
| `assets/source/shadow_background_original.png` | 暗影背景 | 沿用上一版，字节未改 |
| `assets/source/cat_sprite_sheet_original.png` | 小猫动画源 | 沿用上一版，字节未改 |
| `assets/tiles/meteorites/original_sheet.png` | 陨石地砖源 | 原样保存；确定性裁切、清边、透明画布和双色映射 |

本版没有下载在线游戏素材，也没有用生成模型重画陨石。月光/暗影 PNG 保留选中源形态的几何和明暗细节；同名两世界文件共享完全一致的 Alpha 轮廓。

## 权利状态

这些图片由用户在会话中提供。项目记录了来源和技术处理，但无法独立确认作者身份、独占权或商业授权。公开或商业发布前，应由用户/权利人确认所有源图片允许随游戏重新分发。

## 工具披露

- OpenAI Codex：集成代码、测试和文档辅助。
- Pillow：确定性裁切、边缘清理、透明 PNG 和配色变体。
- pygame-ce：运行时缓存与真实游戏渲染。
- Pygbag 0.9.3：浏览器 QA。
- 未调用图像生成模型。
