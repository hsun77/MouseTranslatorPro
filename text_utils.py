from __future__ import annotations

import hashlib
import re


_SPACE_RE = re.compile(r"[ \t\r\f\v]+")
_LINE_RE = re.compile(r"\n{3,}")
_CHINESE_RE = re.compile(r"[\u3400-\u9fff]")


def clean_text(text: str | None) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _SPACE_RE.sub(" ", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    text = _LINE_RE.sub("\n\n", text)
    return text.strip()


def has_chinese(text: str) -> bool:
    return bool(_CHINESE_RE.search(text))


def text_fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def is_probably_meaningful(text: str, min_len: int, max_len: int) -> tuple[bool, str]:
    if not text:
        return False, "empty"
    if len(text) < min_len:
        return False, "too_short"
    if len(text) > max_len:
        return False, "too_long"
    if not any(ch.isalnum() or "\u3040" <= ch <= "\u30ff" or "\u3400" <= ch <= "\u9fff" for ch in text):
        return False, "no_word_characters"
    return True, "ok"
