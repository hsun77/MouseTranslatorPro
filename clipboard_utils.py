from __future__ import annotations

import time
from typing import Optional

import pyautogui
import pyperclip


def get_clipboard_text() -> str:
    try:
        value = pyperclip.paste()
    except pyperclip.PyperclipException:
        return ""
    return value if isinstance(value, str) else ""


def set_clipboard_text(text: str) -> bool:
    try:
        pyperclip.copy(text)
        return True
    except pyperclip.PyperclipException:
        return False


def copy_current_selection(wait_seconds: float = 0.18) -> str:
    pyautogui.hotkey("ctrl", "c")
    time.sleep(wait_seconds)
    return get_clipboard_text()


class ClipboardSnapshot:
    def __init__(self) -> None:
        self.text: Optional[str] = None
        self.available = False

    def capture(self) -> None:
        try:
            self.text = pyperclip.paste()
            self.available = isinstance(self.text, str)
        except pyperclip.PyperclipException:
            self.text = None
            self.available = False

    def restore(self) -> bool:
        if not self.available or self.text is None:
            return False
        return set_clipboard_text(self.text)
