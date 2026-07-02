# MouseTranslatorPro v0.1.0

Initial Windows-only release.

## Highlights

- Real-time mouse selection translation.
- System tray menu with enable/pause, settings, test translation, log viewer, and quit.
- Global hotkeys for toggle, quit, clipboard translation, and OCR mode.
- Translation providers: Google via `deep-translator`, OpenAI, and DeepL.
- PySide6 always-on-top translation popup.
- Optional OCR screenshot workflow using Tesseract.
- Local config file and rotating privacy-conscious logs.
- PyInstaller build script and spec file.

## Notes

- OpenAI and DeepL require API keys through environment variables.
- OCR requires a separate Windows Tesseract OCR installation.
- The app obtains selected text by temporarily simulating `Ctrl+C`.
