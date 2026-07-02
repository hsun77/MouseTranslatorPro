from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QApplication, QWidget


@dataclass(frozen=True)
class OcrResult:
    text: str


class OcrDependencyError(RuntimeError):
    pass


def dependency_help() -> str:
    return (
        "OCR 依赖不可用。请先安装 Python 依赖：pip install pytesseract pillow，"
        "并安装 Tesseract OCR Windows 版，然后把 tesseract.exe 所在目录加入 PATH。"
    )


def recognize_screen_region(left: int, top: int, right: int, bottom: int) -> OcrResult:
    try:
        from PIL import ImageGrab
        import pytesseract
    except ImportError as exc:
        raise OcrDependencyError(dependency_help()) from exc

    if right <= left or bottom <= top:
        return OcrResult("")

    try:
        image = ImageGrab.grab(bbox=(left, top, right, bottom))
        text = pytesseract.image_to_string(image)
    except pytesseract.TesseractNotFoundError as exc:  # type: ignore[attr-defined]
        raise OcrDependencyError(dependency_help()) from exc
    except Exception as exc:
        raise OcrDependencyError(f"OCR 识别失败：{type(exc).__name__}: {exc}") from exc
    return OcrResult(text or "")


class ScreenshotSelector(QWidget):
    selected = Signal(int, int, int, int)
    canceled = Signal()

    def __init__(self) -> None:
        super().__init__(None)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setCursor(Qt.CrossCursor)
        self._start: QPoint | None = None
        self._end: QPoint | None = None

        screens = QApplication.screens()
        if screens:
            geometry = screens[0].geometry()
            for screen in screens[1:]:
                geometry = geometry.united(screen.geometry())
            self.setGeometry(geometry)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            self._start = event.globalPosition().toPoint()
            self._end = self._start
            self.update()

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._start is not None:
            self._end = event.globalPosition().toPoint()
            self.update()

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        if event.button() != Qt.LeftButton or self._start is None:
            return
        self._end = event.globalPosition().toPoint()
        rect = QRect(self._start, self._end).normalized()
        self.hide()
        if rect.width() < 5 or rect.height() < 5:
            self.canceled.emit()
        else:
            self.selected.emit(rect.left(), rect.top(), rect.right(), rect.bottom())
        self.deleteLater()

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        if event.key() == Qt.Key_Escape:
            self.hide()
            self.canceled.emit()
            self.deleteLater()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))
        if self._start is not None and self._end is not None:
            local_start = self.mapFromGlobal(self._start)
            local_end = self.mapFromGlobal(self._end)
            rect = QRect(local_start, local_end).normalized()
            painter.setPen(QPen(QColor(0, 180, 255), 2))
            painter.setBrush(QColor(0, 180, 255, 40))
            painter.drawRect(rect)
