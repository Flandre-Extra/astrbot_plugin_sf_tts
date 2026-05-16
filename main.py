import os
import re
import base64
import uuid
import httpx
from astrbot.api.event import AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.event.filter import on_decorating_result
from astrbot import logger

try:
    from .filter import strip_brackets
except ImportError:
    import filter as _filter_mod
    strip_brackets = _filter_mod.strip_brackets

PRESET_VOICES = ("alex", "anna", "bella", "benjamin", "charles", "claire", "david", "diana")


@register("astrbot_plugin_sf_tts", "FlandreX", "硅基流动 CosyVoice2 TTS", "1.0.0")
class SfTTSPlugin(Star):
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.config = config or {}
        timeout = int(self.config.get("timeout", 120))
        self.client = httpx.AsyncClient(timeout=timeout)
        self._ref_b64 = ""
        self._ref_text = ""

    async def initialize(self):
        if not self.config.get("use_custom_voice"):
            return
        if self.config.get("custom_voice_uri", "").strip():
            if self.config.get("reference_audio_path", "").strip():
                logger.warning("[sf_tts] custom_voice_uri 已填，reference_audio_path 和 reference_text 将被忽略")
            logger.info("[sf_tts] 使用预置音色 URI，跳过本地音频加载")
            return
        ref_path = self.config.get("reference_audio_path", "").strip()
        if ref_path and os.path.exists(ref_path):
            try:
                with open(ref_path, "rb") as f:
                    self._ref_b64 = "data:audio/wav;base64," + base64.b64encode(f.read()).decode("ascii")
                self._ref_text = self.config.get("reference_text", "").strip()
                logger.info(f"[sf_tts] 参考音频已加载: {os.path.getsize(ref_path)}B")
            except Exception as e:
                logger.warning(f"[sf_tts] 加载参考音频失败: {e}")

    @on_decorating_result()
    async def on_decorate(self, event: AstrMessageEvent):
        api_key = self.config.get("api_key", "").strip()
        if not api_key:
            logger.warning("[sf_tts] 未配置 api_key")
            return

        do_filter = self.config.get("bracket_filter", True)
        use_custom = self.config.get("use_custom_voice", False)
        model = self.config.get("model", "") or "FunAudioLLM/CosyVoice2-0.5B"
        api_base = self.config.get("api_base", "") or "https://api.siliconflow.cn/v1/audio/speech"
        speed = float(self.config.get("speed", 1.0))
        gain = float(self.config.get("gain", 0))

        if use_custom:
            uri = self.config.get("custom_voice_uri", "").strip()
            if uri:
                if self.config.get("reference_audio_path", "").strip():
                    logger.warning("[sf_tts] custom_voice_uri 已填，reference_audio_path 和 reference_text 将被忽略")
                voice_param = uri
                ref_text = ""
            elif self._ref_b64:
                voice_param = ""
                ref_text = self._ref_text
            else:
                logger.warning("[sf_tts] 参考音频未加载")
                return
        else:
            preset = self.config.get("preset_voice", "claire")
            if preset not in PRESET_VOICES:
                logger.warning(f"[sf_tts] 未知的 preset_voice: {preset}，已回退为 claire")
                preset = "claire"
            voice_param = f"FunAudioLLM/CosyVoice2-0.5B:{preset}"
            ref_text = ""

        result = event.get_result()
        if not result:
            return

        keep_text = self.config.get("keep_text", False)
        if not keep_text and not result.is_llm_result():
            keep_text = True
            logger.info("[sf_tts] 检测到系统指令，强制保留原文")

        from astrbot.core.message.components import Plain, Record

        body_base = {
            "model": model,
            "voice": voice_param,
            "response_format": "mp3",
            "stream": False,
            "speed": speed,
            "gain": gain,
        }
        if use_custom and not self.config.get("custom_voice_uri", "").strip():
            body_base["references"] = [{"audio": self._ref_b64, "text": ref_text}]

        new_chain = []
        for comp in result.chain:
            if not isinstance(comp, Plain) or not comp.text.strip():
                new_chain.append(comp)
                continue

            text = comp.text
            original = text
            if do_filter:
                text = strip_brackets(text)
            text = re.sub(
                r"[\U0001F000-\U0001FFFF]|[\U00002700-\U000027BF]|[\U0001F300-\U0001F9FF]",
                "", text,
            )
            if not text:
                new_chain.append(comp)
                continue

            tts_ok = False
            try:
                body = {**body_base, "input": text}
                r = await self.client.post(
                    api_base,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=body,
                )
                if r.status_code == 200 and r.content:
                    path = os.path.join(
                        os.environ.get("TEMP", os.path.expanduser("~")),
                        f"sf_tts_{uuid.uuid4().hex}.mp3",
                    )
                    with open(path, "wb") as f:
                        f.write(r.content)
                    new_chain.append(Record(file=path, url=path, text=original))
                    tts_ok = True
                    logger.info(f"[sf_tts] TTS OK {len(r.content)}B, {text[:30]}...")
                elif r.status_code == 200:
                    logger.warning("[sf_tts] API 返回空音频")
                else:
                    logger.warning(f"[sf_tts] API {r.status_code}: {r.text[:300]}")
            except Exception as e:
                logger.error(f"[sf_tts] {type(e).__name__}: {e}")

            if keep_text:
                new_chain.append(Plain(original))
            elif not tts_ok:
                new_chain.append(comp)

        result.chain = new_chain

    async def terminate(self):
        await self.client.aclose()
