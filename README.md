# astrbot_plugin_sf_tts

AstrBot 插件：硅基流动 CosyVoice2 TTS，支持系统预设音色与自定义声音克隆。

## 安装

1. AstrBot Web 面板 → 插件管理 → 上传插件
2. 启用后进入配置页，填入 API Key

## 配置项

| 配置 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `api_key` | string | 空 | API Key（必填） |
| `api_base` | string | 空 | 留空使用默认 |
| `model` | string | 空 | 留空使用默认 |
| `use_custom_voice` | bool | false | 开启使用自定义音色，关闭使用系统预设 |
| `preset_voice` | string | claire | 预设音色：alex / anna / bella / benjamin / charles / claire / david / diana |
| `reference_audio_path` | string | 空 | 自定义模式下生效，本地 wav/mp3 绝对路径 |
| `reference_text` | string | 空 | 自定义模式下生效，音频中实际台词 |
| `keep_text` | bool | false | 开启后在语音消息后附带输入给 TTS 的原文文本，关闭则只发送语音 |
| `bracket_filter` | bool | true | TTS 朗读前过滤括号内容，原文不受影响 |
| `speed` | float | 1.0 | 语速 0.25~4.0 |
| `gain` | float | 0 | 音量 -10~10 |
| `timeout` | int | 30 | 请求超时（秒） |

## 音色模式

### 系统预设

`use_custom_voice` = false，选一个 `preset_voice`，填 Key 即用。

### 自定义声音克隆

`use_custom_voice` = true，填入 `reference_audio_path` 和 `reference_text`。

要求：单人说话，8~15 秒，无背景噪音，wav/mp3/opus 格式。

## 行为说明

- TTS 生成语音 → [keep_text 开启] 语音 + 原文文本 / [keep_text 关闭] 仅语音
- `bracket_filter` 只过滤语音朗读内容，原文文本保持完整

## 注意

- 自定义模式下，参考音频在插件启动时加载一次
