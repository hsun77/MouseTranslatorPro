from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QGuiApplication, QKeyEvent
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)


class TranslationPopup(QWidget):
    def __init__(
        self,
        original: str,
        translated: str,
        show_original: bool,
        popup_seconds: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._original = original
        self._expanded = False
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.close)

        self.setWindowFlags(
            Qt.Tool
            | Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setObjectName("TranslationPopup")
        self.setMinimumWidth(360)
        self.setMaximumWidth(560)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 12)
        root.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("划词翻译")
        title.setObjectName("PopupTitle")
        header.addWidget(title)
        header.addStretch(1)

        self.copy_button = QPushButton("复制译文")
        self.copy_button.clicked.connect(lambda: QApplication.clipboard().setText(translated))
        header.addWidget(self.copy_button)

        close_button = QPushButton("×")
        close_button.setFixedSize(26, 26)
        close_button.clicked.connect(self.close)
        header.addWidget(close_button)
        root.addLayout(header)

        if show_original:
            self.original_label = QLabel(self._folded_original())
            self.original_label.setWordWrap(True)
            self.original_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.original_label.setObjectName("OriginalLabel")
            root.addWidget(self.original_label)

            if len(original) > 300:
                self.expand_button = QPushButton("展开原文")
                self.expand_button.clicked.connect(self._toggle_original)
                root.addWidget(self.expand_button)
            else:
                self.expand_button = None
        else:
            self.original_label = None
            self.expand_button = None

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setObjectName("Separator")
        root.addWidget(separator)

        self.translation_box = QPlainTextEdit()
        self.translation_box.setReadOnly(True)
        self.translation_box.setPlainText(translated)
        self.translation_box.setMinimumHeight(95)
        self.translation_box.setMaximumHeight(260)
        root.addWidget(self.translation_box)

        self.setStyleSheet(
            """
            QWidget#TranslationPopup {
                background: #fbfbf8;
                color: #1f2933;
                border: 1px solid #9aa5b1;
                border-radius: 8px;
            }
            QLabel#PopupTitle {
                font-weight: 700;
                font-size: 14px;
            }
            QLabel#OriginalLabel {
                color: #52606d;
                background: #f0f4f8;
                padding: 8px;
                border-radius: 6px;
            }
            QPlainTextEdit {
                background: #ffffff;
                border: 1px solid #bcccdc;
                border-radius: 6px;
                padding: 8px;
                selection-background-color: #3b82f6;
            }
            QPushButton {
                background: #e6f6ff;
                border: 1px solid #91d5ff;
                border-radius: 5px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: #bae7ff;
            }
            QFrame#Separator {
                color: #d9e2ec;
            }
            """
        )

        if popup_seconds > 0:
            self._timer.start(max(1, int(popup_seconds)) * 1000)

    def _folded_original(self) -> str:
        if len(self._original) <= 300:
            return self._original
        return self._original[:300].rstrip() + "..."

    def _toggle_original(self) -> None:
        if not self.original_label or not self.expand_button:
            return
        self._expanded = not self._expanded
        self.original_label.setText(self._original if self._expanded else self._folded_original())
        self.expand_button.setText("折叠原文" if self._expanded else "展开原文")
        self.adjustSize()

    def enterEvent(self, event) -> None:  # type: ignore[override]
        self._timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        if self._timer.interval() > 0:
            self._timer.start()
        super().leaveEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()
            return
        super().keyPressEvent(event)


class PopupManager:
    def __init__(self) -> None:
        self._current: TranslationPopup | None = None

    def show_popup(
        self,
        original: str,
        translated: str,
        x: int,
        y: int,
        show_original: bool,
        popup_seconds: int,
    ) -> None:
        if self._current is not None:
            self._current.close()
        popup = TranslationPopup(original, translated, show_original, popup_seconds)
        popup.adjustSize()
        popup.move(self._fit_to_screen(QPoint(x + 18, y + 18), popup.sizeHint().width(), popup.sizeHint().height()))
        popup.show()
        popup.raise_()
        self._current = popup

    @staticmethod
    def _fit_to_screen(pos: QPoint, width: int, height: int) -> QPoint:
        screen = QGuiApplication.screenAt(pos) or QGuiApplication.primaryScreen()
        if not screen:
            return pos
        area = screen.availableGeometry()
        x = pos.x()
        y = pos.y()
        if x + width > area.right():
            x = area.right() - width - 12
        if y + height > area.bottom():
            y = y - height - 36
        x = max(area.left() + 8, x)
        y = max(area.top() + 8, y)
        return QPoint(x, y)
