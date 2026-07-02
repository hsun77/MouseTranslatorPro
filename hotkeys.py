from __future__ import annotations

from collections.abc import Callable

from pynput import keyboard


class HotkeyManager:
    def __init__(
        self,
        toggle_enabled: Callable[[], None],
        quit_app: Callable[[], None],
        translate_clipboard: Callable[[], None],
        start_ocr: Callable[[], None],
    ) -> None:
        self._listener: keyboard.GlobalHotKeys | None = None
        self._hotkeys = {
            "<ctrl>+<alt>+t": toggle_enabled,
            "<ctrl>+<alt>+q": quit_app,
            "<ctrl>+<alt>+c": translate_clipboard,
            "<ctrl>+<alt>+o": start_ocr,
        }

    def start(self) -> None:
        if self._listener is not None:
            return
        self._listener = keyboard.GlobalHotKeys(self._hotkeys)
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        if self._listener is None:
            return
        self._listener.stop()
        self._listener = None
