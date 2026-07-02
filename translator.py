from __future__ import annotations

import os
from typing import Any


class TranslationError(RuntimeError):
    pass


def _target_for_deepl(target: str) -> str:
    mapping = {
        "zh": "ZH-HANS",
        "zh-cn": "ZH-HANS",
        "zh-CN": "ZH-HANS",
        "zh-hans": "ZH-HANS",
        "en": "EN-US",
        "en-us": "EN-US",
    }
    return mapping.get(target, target.upper())


def _target_for_google(target: str) -> str:
    mapping = {
        "zh": "zh-CN",
        "zh-cn": "zh-CN",
        "zh-CN": "zh-CN",
        "zh-hans": "zh-CN",
    }
    return mapping.get(target, target)


def translate_text(text: str, config: dict[str, Any]) -> str:
    provider = str(config.get("provider", "google")).lower().strip()
    if provider == "google":
        return _translate_google(text, config)
    if provider == "openai":
        return _translate_openai(text, config)
    if provider == "deepl":
        return _translate_deepl(text, config)
    raise TranslationError(f"Unsupported provider: {provider}")


def _translate_google(text: str, config: dict[str, Any]) -> str:
    try:
        from deep_translator import GoogleTranslator
    except ImportError as exc:
        raise TranslationError(
            "缺少 deep-translator 依赖。请运行：pip install -r requirements.txt"
        ) from exc

    source = str(config.get("source_language", "auto") or "auto")
    target = _target_for_google(str(config.get("target_language", "zh-CN") or "zh-CN"))
    try:
        translated = GoogleTranslator(source=source, target=target).translate(text)
    except Exception as exc:
        raise TranslationError(f"Google 翻译失败：{type(exc).__name__}: {exc}") from exc
    return translated or ""


def _translate_openai(text: str, config: dict[str, Any]) -> str:
    key_env = str(config.get("openai_api_key_env", "OPENAI_API_KEY") or "OPENAI_API_KEY")
    api_key = os.getenv(key_env)
    if not api_key:
        raise TranslationError(f"未找到 OpenAI API Key。请先设置环境变量 {key_env}。")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise TranslationError("缺少 openai 依赖。请运行：pip install -r requirements.txt") from exc

    target = str(config.get("target_language", "zh-CN") or "zh-CN")
    model = str(config.get("openai_model", "gpt-4.1-mini") or "gpt-4.1-mini")
    system_prompt = (
        "You are a precise translation engine. Only output the translated text. "
        "Do not explain, do not add quotes. Preserve professional terms, code, URLs, "
        "numbers, and formatting when appropriate. If the input is already Chinese, "
        "return it unchanged."
    )
    user_prompt = f"Translate the following text to {target}:\n\n{text}"

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )
    except Exception as exc:
        raise TranslationError(f"OpenAI 翻译失败：{type(exc).__name__}: {exc}") from exc
    return (response.choices[0].message.content or "").strip()


def _translate_deepl(text: str, config: dict[str, Any]) -> str:
    key_env = str(config.get("deepl_api_key_env", "DEEPL_API_KEY") or "DEEPL_API_KEY")
    api_key = os.getenv(key_env)
    if not api_key:
        raise TranslationError(f"未找到 DeepL API Key。请先设置环境变量 {key_env}。")

    try:
        import deepl
    except ImportError as exc:
        raise TranslationError("缺少 deepl 依赖。请运行：pip install -r requirements.txt") from exc

    target = _target_for_deepl(str(config.get("target_language", "zh-CN") or "zh-CN"))
    source = str(config.get("source_language", "auto") or "auto")
    source_lang = None if source.lower() == "auto" else source.upper()
    try:
        translator = deepl.Translator(api_key)
        result = translator.translate_text(text, source_lang=source_lang, target_lang=target)
    except Exception as exc:
        raise TranslationError(f"DeepL 翻译失败：{type(exc).__name__}: {exc}") from exc
    return str(result.text or "").strip()
