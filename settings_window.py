from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class SettingsWindow(QWidget):
    def __init__(self, config: dict[str, Any], on_save: Callable[[dict[str, Any]], None]) -> None:
        super().__init__()
        self.setWindowTitle("MouseTranslatorPro 设置")
        self.setMinimumWidth(430)
        self._on_save = on_save
        self._config = config.copy()

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.enabled_box = QCheckBox("启用划词翻译")
        self.enabled_box.setChecked(bool(config.get("enabled", True)))
        form.addRow("状态", self.enabled_box)

        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["google", "baidu", "youdao", "tencent", "openai", "deepl"])
        self.provider_combo.setCurrentText(str(config.get("provider", "google")))
        form.addRow("翻译服务", self.provider_combo)

        self.target_combo = QComboBox()
        self.target_combo.setEditable(True)
        self.target_combo.addItems(["zh-CN", "zh-TW", "en", "ja", "ko", "fr", "de", "es"])
        self.target_combo.setCurrentText(str(config.get("target_language", "zh-CN")))
        form.addRow("目标语言", self.target_combo)

        self.popup_seconds = QSpinBox()
        self.popup_seconds.setRange(1, 120)
        self.popup_seconds.setValue(int(config.get("popup_seconds", 8)))
        form.addRow("弹窗停留秒数", self.popup_seconds)

        self.min_length = QSpinBox()
        self.min_length.setRange(1, 200)
        self.min_length.setValue(int(config.get("min_text_length", 2)))
        form.addRow("最小触发字符数", self.min_length)

        self.restore_clipboard = QCheckBox("翻译后尽量恢复原剪贴板文本")
        self.restore_clipboard.setChecked(bool(config.get("restore_clipboard", True)))
        form.addRow("剪贴板", self.restore_clipboard)

        self.show_original = QCheckBox("弹窗显示原文")
        self.show_original.setChecked(bool(config.get("show_original", True)))
        form.addRow("原文", self.show_original)

        self.skip_chinese = QCheckBox("选中文本包含中文时不触发翻译")
        self.skip_chinese.setChecked(bool(config.get("skip_chinese", False)))
        form.addRow("中文文本", self.skip_chinese)

        self.ocr_enabled = QCheckBox("启用 OCR 截图翻译入口")
        self.ocr_enabled.setChecked(bool(config.get("ocr_enabled", False)))
        form.addRow("OCR", self.ocr_enabled)

        layout.addLayout(form)
        hint = QLabel("保存后立即生效。API Key 请通过系统环境变量配置，不会写入配置文件。")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton("取消")
        cancel.clicked.connect(self.close)
        save = QPushButton("保存")
        save.clicked.connect(self._save)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

    def _save(self) -> None:
        updated = self._config.copy()
        updated.update(
            {
                "enabled": self.enabled_box.isChecked(),
                "provider": self.provider_combo.currentText().strip(),
                "target_language": self.target_combo.currentText().strip() or "zh-CN",
                "popup_seconds": int(self.popup_seconds.value()),
                "min_text_length": int(self.min_length.value()),
                "restore_clipboard": self.restore_clipboard.isChecked(),
                "show_original": self.show_original.isChecked(),
                "skip_chinese": self.skip_chinese.isChecked(),
                "ocr_enabled": self.ocr_enabled.isChecked(),
            }
        )
        self._on_save(updated)
        self.close()
