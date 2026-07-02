from __future__ import annotations

import json
from pathlib import Path
from typing import Any


APP_DIR = Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / "config.json"


DEFAULT_CONFIG: dict[str, Any] = {
    "enabled": True,
    "target_language": "zh-CN",
    "source_language": "auto",
    "provider": "google",
    "popup_seconds": 8,
    "min_text_length": 2,
    "max_text_length": 4000,
    "debounce_ms": 700,
    "restore_clipboard": True,
    "show_original": True,
    "skip_chinese": False,
    "ocr_enabled": False,
    "ocr_engine": "tesseract",
    "openai_model": "gpt-4.1-mini",
    "deepl_api_key_env": "DEEPL_API_KEY",
    "openai_api_key_env": "OPENAI_API_KEY",
    "baidu_app_id_env": "BAIDU_TRANSLATE_APP_ID",
    "baidu_secret_key_env": "BAIDU_TRANSLATE_SECRET_KEY",
    "youdao_app_key_env": "YOUDAO_APP_KEY",
    "youdao_app_secret_env": "YOUDAO_APP_SECRET",
    "tencent_secret_id_env": "TENCENTCLOUD_SECRET_ID",
    "tencent_secret_key_env": "TENCENTCLOUD_SECRET_KEY",
    "tencent_region": "ap-guangzhou",
    "tencent_project_id": 0,
}


def ensure_config(path: Path = CONFIG_PATH) -> Path:
    if not path.exists():
        save_config(DEFAULT_CONFIG.copy(), path)
    return path


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    ensure_config(path)
    try:
        with path.open("r", encoding="utf-8") as f:
            loaded = json.load(f)
    except (OSError, json.JSONDecodeError):
        loaded = {}

    config = DEFAULT_CONFIG.copy()
    if isinstance(loaded, dict):
        config.update(loaded)
    return config


def save_config(config: dict[str, Any], path: Path = CONFIG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
        f.write("\n")
