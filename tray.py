from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QMenu, QSystemTrayIcon


def create_icon() -> QIcon:
    pixmap = QPixmap(QSize(64, 64))
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(Qt.GlobalColor.darkCyan)
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(4, 4, 56, 56, 12, 12)
    painter.setPen(Qt.GlobalColor.white)
    font = painter.font()
    font.setBold(True)
    font.setPointSize(24)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "译")
    painter.end()
    return QIcon(pixmap)


class TrayController:
    def __init__(
        self,
        enabled: bool,
        toggle_enabled: Callable[[], None],
        open_settings: Callable[[], None],
        test_translation: Callable[[], None],
        open_log: Callable[[], None],
        quit_app: Callable[[], None],
        app_dir: Path,
    ) -> None:
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(create_icon())
        self.tray.setToolTip("MouseTranslatorPro")

        menu = QMenu()
        self.toggle_action = QAction(self._toggle_text(enabled), menu)
        self.toggle_action.triggered.connect(toggle_enabled)
        menu.addAction(self.toggle_action)

        settings_action = QAction("打开设置", menu)
        settings_action.triggered.connect(open_settings)
        menu.addAction(settings_action)

        test_action = QAction("测试翻译", menu)
        test_action.triggered.connect(test_translation)
        menu.addAction(test_action)

        log_action = QAction("查看日志", menu)
        log_action.triggered.connect(open_log)
        menu.addAction(log_action)

        menu.addSeparator()
        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(quit_app)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)

    @staticmethod
    def _toggle_text(enabled: bool) -> str:
        return "暂停划词翻译" if enabled else "启用划词翻译"

    def set_enabled(self, enabled: bool) -> None:
        self.toggle_action.setText(self._toggle_text(enabled))
        self.tray.setToolTip(f"MouseTranslatorPro - {'已启用' if enabled else '已暂停'}")

    def show(self) -> None:
        self.tray.show()

    def hide(self) -> None:
        self.tray.hide()
