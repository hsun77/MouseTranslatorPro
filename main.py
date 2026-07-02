from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app_controller import AppController
from config_manager import ensure_config


def main() -> int:
    app_dir = Path(__file__).resolve().parent
    ensure_config()

    app = QApplication(sys.argv)
    app.setApplicationName("MouseTranslatorPro")
    app.setQuitOnLastWindowClosed(False)

    controller = AppController(app, app_dir)
    controller.start()
    app.aboutToQuit.connect(controller.quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
