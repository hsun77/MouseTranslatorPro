from __future__ import annotations

import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication

from clipboard_utils import ClipboardSnapshot, copy_current_selection, get_clipboard_text
from config_manager import CONFIG_PATH, load_config, save_config
from hotkeys import HotkeyManager
from logger_setup import setup_logger
from mouse_listener import MouseSelectionListener
from ocr_utils import OcrDependencyError, ScreenshotSelector, recognize_screen_region
from popup import PopupManager
from settings_window import SettingsWindow
from text_utils import clean_text, has_chinese, is_probably_meaningful, text_fingerprint
from translator import TranslationError, translate_text
from tray import TrayController


class AppController(QObject):
    request_selection = Signal(int, int)
    show_popup_signal = Signal(str, str, int, int)
    toggle_signal = Signal()
    quit_signal = Signal()
    clipboard_signal = Signal()
    ocr_signal = Signal()
    ocr_bbox_signal = Signal(int, int, int, int)

    def __init__(self, app: QApplication, app_dir: Path) -> None:
        super().__init__()
        self.app = app
        self.app_dir = app_dir
        self.config = load_config(CONFIG_PATH)
        self.logger = setup_logger(app_dir)
        self.executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="translator")
        self.popup_manager = PopupManager()
        self.settings_window: SettingsWindow | None = None
        self.ocr_selector: ScreenshotSelector | None = None
        self._last_fingerprint = ""
        self._last_time = 0.0
        self._state_lock = threading.Lock()
        self._shutting_down = False

        self.request_selection.connect(self._handle_selection_release)
        self.show_popup_signal.connect(self._show_popup)
        self.toggle_signal.connect(self.toggle_enabled)
        self.quit_signal.connect(self.quit)
        self.clipboard_signal.connect(self.translate_clipboard)
        self.ocr_signal.connect(self.start_ocr_capture)
        self.ocr_bbox_signal.connect(self._handle_ocr_bbox)

        self.mouse_listener = MouseSelectionListener(lambda x, y: self.request_selection.emit(x, y))
        self.hotkeys = HotkeyManager(
            toggle_enabled=lambda: self.toggle_signal.emit(),
            quit_app=lambda: self.quit_signal.emit(),
            translate_clipboard=lambda: self.clipboard_signal.emit(),
            start_ocr=lambda: self.ocr_signal.emit(),
        )
        self.tray = TrayController(
            enabled=bool(self.config.get("enabled", True)),
            toggle_enabled=self.toggle_enabled,
            open_settings=self.open_settings,
            test_translation=self.test_translation,
            open_log=self.open_log,
            quit_app=self.quit,
            app_dir=app_dir,
        )

    def start(self) -> None:
        self.logger.info("application_started")
        self.mouse_listener.start()
        self.hotkeys.start()
        self.tray.show()

    @Slot(int, int)
    def _handle_selection_release(self, x: int, y: int) -> None:
        if self._shutting_down or not self.config.get("enabled", True):
            return
        self.executor.submit(self._selection_worker, x, y)

    def _selection_worker(self, x: int, y: int) -> None:
        time.sleep(0.18)
        snapshot = ClipboardSnapshot()
        snapshot.capture()
        selected = ""
        try:
            selected = copy_current_selection(wait_seconds=0.08)
        except Exception as exc:
            self.logger.warning("copy_selection_failed error=%s", type(exc).__name__)
            return
        finally:
            if self.config.get("restore_clipboard", True) or not selected:
                try:
                    if not snapshot.restore():
                        self.logger.info("clipboard_restore_skipped")
                except Exception as exc:
                    self.logger.warning("clipboard_restore_failed error=%s", type(exc).__name__)

        self._process_text(selected, x, y, source="selection")

    def _process_text(self, raw_text: str, x: int, y: int, source: str) -> None:
        text = clean_text(raw_text)
        min_len = int(self.config.get("min_text_length", 2))
        max_len = int(self.config.get("max_text_length", 4000))
        ok, reason = is_probably_meaningful(text, min_len, max_len)
        if not ok:
            self.logger.info("text_ignored source=%s reason=%s length=%d", source, reason, len(text))
            return

        if self.config.get("skip_chinese", False) and has_chinese(text):
            self.logger.info("text_ignored source=%s reason=contains_chinese length=%d", source, len(text))
            return

        now = time.monotonic()
        fp = text_fingerprint(text)
        debounce = max(0, int(self.config.get("debounce_ms", 700))) / 1000.0
        with self._state_lock:
            if fp == self._last_fingerprint and now - self._last_time < debounce:
                self.logger.info("text_ignored source=%s reason=duplicate length=%d", source, len(text))
                return
            self._last_fingerprint = fp
            self._last_time = now

        self.logger.info(
            "translation_started source=%s provider=%s length=%d",
            source,
            self.config.get("provider", "google"),
            len(text),
        )
        try:
            translated = translate_text(text, self.config.copy())
        except TranslationError as exc:
            translated = f"翻译失败：{exc}"
            self.logger.warning(
                "provider_error provider=%s error=%s length=%d",
                self.config.get("provider", "google"),
                type(exc).__name__,
                len(text),
            )
        except Exception as exc:
            translated = f"翻译失败：{type(exc).__name__}: {exc}"
            self.logger.exception("unexpected_translation_error length=%d", len(text))

        if translated:
            self.show_popup_signal.emit(text, translated, x, y)

    @Slot(str, str, int, int)
    def _show_popup(self, original: str, translated: str, x: int, y: int) -> None:
        self.popup_manager.show_popup(
            original=original,
            translated=translated,
            x=x,
            y=y,
            show_original=bool(self.config.get("show_original", True)),
            popup_seconds=int(self.config.get("popup_seconds", 8)),
        )

    @Slot()
    def toggle_enabled(self) -> None:
        self.config["enabled"] = not bool(self.config.get("enabled", True))
        save_config(self.config, CONFIG_PATH)
        self.tray.set_enabled(bool(self.config["enabled"]))
        self.logger.info("enabled_changed enabled=%s", self.config["enabled"])

    @Slot()
    def translate_clipboard(self) -> None:
        pos = QCursor.pos()
        text = get_clipboard_text()
        self.executor.submit(self._process_text, text, pos.x(), pos.y(), "clipboard")

    @Slot()
    def start_ocr_capture(self) -> None:
        if self.ocr_selector is not None:
            return
        self.ocr_selector = ScreenshotSelector()
        self.ocr_selector.selected.connect(self.ocr_bbox_signal.emit)
        self.ocr_selector.canceled.connect(lambda: setattr(self, "ocr_selector", None))
        self.ocr_selector.showFullScreen()
        self.logger.info("ocr_capture_started")

    @Slot(int, int, int, int)
    def _handle_ocr_bbox(self, left: int, top: int, right: int, bottom: int) -> None:
        self.ocr_selector = None
        pos = QCursor.pos()
        self.executor.submit(self._ocr_worker, left, top, right, bottom, pos.x(), pos.y())

    def _ocr_worker(self, left: int, top: int, right: int, bottom: int, x: int, y: int) -> None:
        try:
            result = recognize_screen_region(left, top, right, bottom)
        except OcrDependencyError as exc:
            self.logger.warning("ocr_dependency_error error=%s", type(exc).__name__)
            self.show_popup_signal.emit("OCR", str(exc), x, y)
            return
        except Exception as exc:
            self.logger.exception("ocr_unexpected_error")
            self.show_popup_signal.emit("OCR", f"OCR 失败：{type(exc).__name__}: {exc}", x, y)
            return
        self._process_text(result.text, x, y, source="ocr")

    def open_settings(self) -> None:
        if self.settings_window is not None:
            self.settings_window.raise_()
            self.settings_window.activateWindow()
            return
        self.settings_window = SettingsWindow(self.config, self._save_settings)
        self.settings_window.destroyed.connect(lambda: setattr(self, "settings_window", None))
        self.settings_window.show()

    def _save_settings(self, updated: dict[str, Any]) -> None:
        self.config = updated.copy()
        save_config(self.config, CONFIG_PATH)
        self.tray.set_enabled(bool(self.config.get("enabled", True)))
        self.logger.info("settings_saved")

    def test_translation(self) -> None:
        pos = QCursor.pos()
        self.executor.submit(
            self._process_text,
            "Hello, this is a MouseTranslatorPro test.",
            pos.x(),
            pos.y(),
            "test",
        )

    def open_log(self) -> None:
        log_path = self.app_dir / "logs" / "app.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.touch(exist_ok=True)
        try:
            os.startfile(str(log_path))  # type: ignore[attr-defined]
        except Exception as exc:
            pos = QCursor.pos()
            self.show_popup_signal.emit("日志", f"无法打开日志：{type(exc).__name__}: {exc}", pos.x(), pos.y())

    @Slot()
    def quit(self) -> None:
        if self._shutting_down:
            return
        self._shutting_down = True
        self.logger.info("application_exiting")
        try:
            self.mouse_listener.stop()
            self.hotkeys.stop()
            self.tray.hide()
        finally:
            self.executor.shutdown(wait=False, cancel_futures=True)
            self.app.quit()
