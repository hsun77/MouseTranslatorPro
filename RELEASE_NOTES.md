# MouseTranslatorPro v0.2.1

Friend-ready packaging update.

## Fixed

- Packaged EXE now writes `config.json` and logs next to `MouseTranslatorPro.exe`, so an unzipped folder can be used directly.

## Packaging

- Added a friend-facing quick start guide.
- Added a Chinese launch batch file.
- Prepared a ready-to-send zip for Google, Tencent Cloud TMT, and Youdao usage.

---

# MouseTranslatorPro v0.2.0

Adds domestic translation providers.

## New

- Added Baidu Translate provider through Baidu Translate Open Platform API.
- Added Youdao Zhiyun provider through Youdao text translation API.
- Added Tencent Cloud TMT provider through Tencent Cloud SDK.
- Added provider choices to the settings window.
- Added domestic provider environment variable documentation.

## Required environment variables

- Baidu: `BAIDU_TRANSLATE_APP_ID`, `BAIDU_TRANSLATE_SECRET_KEY`
- Youdao: `YOUDAO_APP_KEY`, `YOUDAO_APP_SECRET`
- Tencent Cloud: `TENCENTCLOUD_SECRET_ID`, `TENCENTCLOUD_SECRET_KEY`

---

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
