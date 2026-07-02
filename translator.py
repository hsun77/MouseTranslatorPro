from __future__ import annotations

import os
import hashlib
import time
import uuid
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


def _lang_for_baidu(language: str, *, source: bool = False) -> str:
    normalized = (language or "auto").strip()
    lower = normalized.lower()
    mapping = {
        "auto": "auto",
        "zh": "zh",
        "zh-cn": "zh",
        "zh-hans": "zh",
        "zh-CN": "zh",
        "zh-tw": "cht",
        "zh-hant": "cht",
        "en": "en",
        "ja": "jp",
        "jp": "jp",
        "ko": "kor",
        "kr": "kor",
        "fr": "fra",
        "de": "de",
        "es": "spa",
        "ru": "ru",
        "pt": "pt",
        "it": "it",
        "vi": "vie",
        "th": "th",
        "ar": "ara",
    }
    if source and lower == "auto":
        return "auto"
    return mapping.get(lower, normalized)


def _lang_for_youdao(language: str, *, source: bool = False) -> str:
    normalized = (language or "auto").strip()
    lower = normalized.lower()
    mapping = {
        "auto": "auto",
        "zh": "zh-CHS",
        "zh-cn": "zh-CHS",
        "zh-hans": "zh-CHS",
        "zh-CN": "zh-CHS",
        "zh-tw": "zh-CHT",
        "zh-hant": "zh-CHT",
        "en": "en",
        "ja": "ja",
        "jp": "ja",
        "ko": "ko",
        "kr": "ko",
        "fr": "fr",
        "de": "de",
        "es": "es",
        "ru": "ru",
        "pt": "pt",
        "it": "it",
        "vi": "vi",
        "id": "id",
        "ar": "ar",
    }
    if source and lower == "auto":
        return "auto"
    return mapping.get(lower, normalized)


def _lang_for_tencent(language: str, *, source: bool = False) -> str:
    normalized = (language or "auto").strip()
    lower = normalized.lower()
    mapping = {
        "auto": "auto",
        "zh": "zh",
        "zh-cn": "zh",
        "zh-hans": "zh",
        "zh-CN": "zh",
        "zh-tw": "zh-TW",
        "zh-hant": "zh-TW",
        "en": "en",
        "ja": "ja",
        "jp": "ja",
        "ko": "ko",
        "kr": "ko",
        "fr": "fr",
        "de": "de",
        "es": "es",
        "ru": "ru",
        "pt": "pt",
        "it": "it",
        "vi": "vi",
        "id": "id",
        "th": "th",
        "ms": "ms",
        "ar": "ar",
        "hi": "hi",
    }
    if source and lower == "auto":
        return "auto"
    return mapping.get(lower, normalized)


def translate_text(text: str, config: dict[str, Any]) -> str:
    provider = str(config.get("provider", "google")).lower().strip()
    if provider == "google":
        return _translate_google(text, config)
    if provider == "openai":
        return _translate_openai(text, config)
    if provider == "deepl":
        return _translate_deepl(text, config)
    if provider == "baidu":
        return _translate_baidu(text, config)
    if provider == "youdao":
        return _translate_youdao(text, config)
    if provider == "tencent":
        return _translate_tencent(text, config)
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


def _translate_baidu(text: str, config: dict[str, Any]) -> str:
    app_id_env = str(config.get("baidu_app_id_env", "BAIDU_TRANSLATE_APP_ID") or "BAIDU_TRANSLATE_APP_ID")
    secret_env = str(config.get("baidu_secret_key_env", "BAIDU_TRANSLATE_SECRET_KEY") or "BAIDU_TRANSLATE_SECRET_KEY")
    app_id = os.getenv(app_id_env)
    secret_key = os.getenv(secret_env)
    if not app_id or not secret_key:
        raise TranslationError(f"未找到百度翻译凭据。请设置环境变量 {app_id_env} 和 {secret_env}。")

    try:
        import requests
    except ImportError as exc:
        raise TranslationError("缺少 requests 依赖。请运行：pip install -r requirements.txt") from exc

    salt = str(uuid.uuid4())
    sign_raw = f"{app_id}{text}{salt}{secret_key}"
    sign = hashlib.md5(sign_raw.encode("utf-8")).hexdigest()
    source = _lang_for_baidu(str(config.get("source_language", "auto")), source=True)
    target = _lang_for_baidu(str(config.get("target_language", "zh-CN")))
    payload = {
        "q": text,
        "from": source,
        "to": target,
        "appid": app_id,
        "salt": salt,
        "sign": sign,
    }
    try:
        response = requests.post("https://fanyi-api.baidu.com/api/trans/vip/translate", data=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        raise TranslationError(f"百度翻译请求失败：{type(exc).__name__}: {exc}") from exc

    if "error_code" in data:
        raise TranslationError(f"百度翻译失败：{data.get('error_code')} {data.get('error_msg', '')}".strip())
    results = data.get("trans_result") or []
    translated_parts = [str(item.get("dst", "")) for item in results if item.get("dst")]
    return "\n".join(translated_parts).strip()


def _youdao_input(text: str) -> str:
    if len(text) <= 20:
        return text
    return f"{text[:10]}{len(text)}{text[-10:]}"


def _translate_youdao(text: str, config: dict[str, Any]) -> str:
    app_key_env = str(config.get("youdao_app_key_env", "YOUDAO_APP_KEY") or "YOUDAO_APP_KEY")
    secret_env = str(config.get("youdao_app_secret_env", "YOUDAO_APP_SECRET") or "YOUDAO_APP_SECRET")
    app_key = os.getenv(app_key_env)
    app_secret = os.getenv(secret_env)
    if not app_key or not app_secret:
        raise TranslationError(f"未找到有道智云凭据。请设置环境变量 {app_key_env} 和 {secret_env}。")

    try:
        import requests
    except ImportError as exc:
        raise TranslationError("缺少 requests 依赖。请运行：pip install -r requirements.txt") from exc

    salt = str(uuid.uuid4())
    curtime = str(int(time.time()))
    input_text = _youdao_input(text)
    sign_raw = f"{app_key}{input_text}{salt}{curtime}{app_secret}"
    sign = hashlib.sha256(sign_raw.encode("utf-8")).hexdigest()
    payload = {
        "q": text,
        "from": _lang_for_youdao(str(config.get("source_language", "auto")), source=True),
        "to": _lang_for_youdao(str(config.get("target_language", "zh-CN"))),
        "appKey": app_key,
        "salt": salt,
        "sign": sign,
        "signType": "v3",
        "curtime": curtime,
    }
    try:
        response = requests.post("https://openapi.youdao.com/api", data=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        raise TranslationError(f"有道智云请求失败：{type(exc).__name__}: {exc}") from exc

    error_code = str(data.get("errorCode", ""))
    if error_code != "0":
        raise TranslationError(f"有道智云翻译失败：errorCode={error_code}")
    translated = data.get("translation") or []
    return "\n".join(str(item) for item in translated).strip()


def _translate_tencent(text: str, config: dict[str, Any]) -> str:
    secret_id_env = str(config.get("tencent_secret_id_env", "TENCENTCLOUD_SECRET_ID") or "TENCENTCLOUD_SECRET_ID")
    secret_key_env = str(config.get("tencent_secret_key_env", "TENCENTCLOUD_SECRET_KEY") or "TENCENTCLOUD_SECRET_KEY")
    secret_id = os.getenv(secret_id_env)
    secret_key = os.getenv(secret_key_env)
    if not secret_id or not secret_key:
        raise TranslationError(f"未找到腾讯云凭据。请设置环境变量 {secret_id_env} 和 {secret_key_env}。")

    try:
        from tencentcloud.common import credential
        from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
        from tencentcloud.tmt.v20180321 import models, tmt_client
    except ImportError as exc:
        raise TranslationError("缺少 tencentcloud-sdk-python 依赖。请运行：pip install -r requirements.txt") from exc

    region = str(config.get("tencent_region", "ap-guangzhou") or "ap-guangzhou")
    project_id = int(config.get("tencent_project_id", 0) or 0)
    req = models.TextTranslateRequest()
    req.SourceText = text
    req.Source = _lang_for_tencent(str(config.get("source_language", "auto")), source=True)
    req.Target = _lang_for_tencent(str(config.get("target_language", "zh-CN")))
    req.ProjectId = project_id

    try:
        cred = credential.Credential(secret_id, secret_key)
        client = tmt_client.TmtClient(cred, region)
        response = client.TextTranslate(req)
    except TencentCloudSDKException as exc:
        raise TranslationError(f"腾讯云翻译失败：{exc.code}: {exc.message}") from exc
    except Exception as exc:
        raise TranslationError(f"腾讯云翻译请求失败：{type(exc).__name__}: {exc}") from exc
    return str(getattr(response, "TargetText", "") or "").strip()
