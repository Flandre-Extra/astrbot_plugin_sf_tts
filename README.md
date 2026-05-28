# astrbot_plugin_sf_tts

AstrBot 插件：硅基流动 CosyVoice2 TTS，支持系统预设音色、预置 URI 与自定义声音克隆。

v1.0.8 | 仓库: https://github.com/Flandre-Extra/astrbot_plugin_sf_tts

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
| `custom_voice_uri` | string | 空 | 预置音色 URI（speech:xxx:xxx:xxx），填了用 URI 轻量调用，不填走 references 内联 base64。需实名认证。与 reference_audio_path 同时填写时后者被忽略并打印 warn |
| `reference_audio_path` | string | 空 | 自定义模式下生效，本地 wav/mp3 绝对路径 |
| `reference_text` | string | 空 | 自定义模式下生效，音频中实际台词 |
| `keep_text` | bool | false | 附带原文（系统指令如 /reset 自动强制开启） |
| `text_filter_regex` | string | 空 | 自定义正则过滤 TTS 文本，匹配到的内容被移除。空则不过滤 |
| `speed` | float | 1.0 | 语速 0.25~4.0 |
| `gain` | float | 0 | 音量 -10~10 |
| `timeout` | int | 120 | 请求超时（秒），长文本需 60s+ |

## 音色模式

### 系统预设

`use_custom_voice` = false，选一个 `preset_voice`，填 Key 即用。

### 预置音色 URI（推荐）

1. 上传参考音频获取 URI：

```bash
curl -X POST https://api.siliconflow.cn/v1/uploads/audio/voice \
  -H "Authorization: Bearer sk-xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "FunAudioLLM/CosyVoice2-0.5B",
    "customName": "你的音色名",
    "audio": "data:audio/wav;base64,...",
    "text": "参考音频中的台词"
  }'
```

2. 返回 `{"uri": "speech:能代:xxx:xxx"}`，填入 `custom_voice_uri`

3. 后续请求只传 URI 字符串，无需每次传 850KB base64

> 需硅基流动实名认证。

### 本地 references 模式

`use_custom_voice` = true，不填 `custom_voice_uri`，填入 `reference_audio_path` 和 `reference_text`。

要求：单人说话，8~15 秒，无背景噪音，wav/mp3/opus 格式。每次请求内联 base64 传输。

## 行为说明

- TTS 生成语音 → keep_text 开启：语音 + 原文 / keep_text 关闭：仅语音
- 系统指令（/reset /sid 等）自动强制保留原文，不受 keep_text 开关影响
- 主动消息不会被误判为系统指令，严格遵从 `keep_text` 配置（v1.0.8）
- `text_filter_regex` 只过滤语音朗读内容，原文文本保持完整
- TTS 失败时原文不会被丢弃（v1.0.2+）

## 注意

- 预置 URI 模式下参考音频存在硅基服务端，references 模式下音频每次内联传输不落盘
- 自定义模式下，references 模式的本地音频在插件启动时加载一次并缓存
