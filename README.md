# MouseTranslatorPro

MouseTranslatorPro 是一个 Windows 11 桌面端实时鼠标划词翻译工具。用户在任意 Windows 软件中用鼠标选中文字并松开左键后，程序会短暂等待，模拟 `Ctrl+C` 获取当前选区，调用用户配置的翻译服务，并在鼠标附近弹出 always-on-top 翻译窗口。

## 功能介绍

- 鼠标划词后自动翻译，默认翻译成简体中文。
- 后台运行，系统托盘菜单可暂停、恢复、打开设置、测试翻译、查看日志和退出。
- 全局快捷键：
  - `Ctrl+Alt+T`：启用/暂停划词翻译。
  - `Ctrl+Alt+Q`：退出程序。
  - `Ctrl+Alt+C`：翻译当前剪贴板文本。
  - `Ctrl+Alt+O`：进入 OCR 截图翻译模式。
- 弹窗显示原文和译文，原文默认折叠到前 300 字，译文可复制。
- 弹窗默认 8 秒自动关闭，鼠标悬停时暂停自动关闭，`Esc` 可关闭。
- 支持 `google`、`openai`、`deepl` 三种 provider。
- OCR 为可选功能，缺少依赖或系统 Tesseract 时会显示安装提示，不影响普通划词翻译。
- 日志自动轮转，最多保留 3 个日志文件，日志不记录完整选中文本。

## 安装方法

建议使用 Python 3.10+：

```powershell
cd /d D:\MouseTranslatorPro
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

如果不想创建虚拟环境，也可以直接在系统 Python 中安装依赖：

```powershell
cd /d D:\MouseTranslatorPro
pip install -r requirements.txt
```

## 运行方法

命令行运行：

```powershell
cd /d D:\MouseTranslatorPro
python main.py
```

也可以双击：

```text
run_mouse_translator.bat
```

启动后程序会进入系统托盘。右键托盘图标可打开菜单。

## 配置说明

首次启动会自动生成 `config.json`。示例配置见 `config.example.json`：

```json
{
  "enabled": true,
  "target_language": "zh-CN",
  "source_language": "auto",
  "provider": "google",
  "popup_seconds": 8,
  "min_text_length": 2,
  "max_text_length": 4000,
  "debounce_ms": 700,
  "restore_clipboard": true,
  "show_original": true,
  "skip_chinese": false,
  "ocr_enabled": false,
  "ocr_engine": "tesseract",
  "openai_model": "gpt-4.1-mini",
  "deepl_api_key_env": "DEEPL_API_KEY",
  "openai_api_key_env": "OPENAI_API_KEY"
}
```

主要配置项：

- `enabled`：是否启用划词翻译。
- `provider`：翻译服务，支持 `google`、`openai`、`deepl`。
- `target_language`：目标语言，默认 `zh-CN`。
- `popup_seconds`：弹窗自动关闭时间。
- `min_text_length` / `max_text_length`：触发翻译的文本长度范围。
- `debounce_ms`：重复文本防抖时间。
- `restore_clipboard`：是否尽量恢复原剪贴板文本。
- `show_original`：弹窗是否显示原文。
- `skip_chinese`：包含中文时是否跳过翻译。
- `ocr_enabled`：OCR 入口开关配置；快捷键仍会做依赖检查并提示。

## 翻译 Provider 说明

### google

默认 provider，使用 `deep-translator` 的 `GoogleTranslator`：

```json
{
  "provider": "google",
  "source_language": "auto",
  "target_language": "zh-CN"
}
```

该方式不需要 API Key，但实际可用性取决于网络环境和第三方库。

### openai

使用 OpenAI Python SDK。API Key 只从环境变量读取，不会写入代码或配置文件。

设置环境变量：

```powershell
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "你的 key", "User")
```

重新打开终端或重启程序后生效。默认模型由 `openai_model` 指定。

### deepl

使用 DeepL 官方 Python 包。API Key 只从环境变量读取。

设置环境变量：

```powershell
[Environment]::SetEnvironmentVariable("DEEPL_API_KEY", "你的 key", "User")
```

没有 key 时，程序会在弹窗里显示明确错误，不会崩溃。

## OCR 安装说明

OCR 是可选功能。Python 依赖已写入 `requirements.txt`：

```powershell
pip install pytesseract pillow
```

还需要安装 Windows 版 Tesseract OCR，并把 `tesseract.exe` 所在目录加入 `PATH`。如果未安装或不可用，按 `Ctrl+Alt+O` 后程序会显示安装提示而不是崩溃。

## 打包 exe 方法

打包前先安装依赖，然后运行：

```powershell
cd /d D:\MouseTranslatorPro
.\build_exe.bat
```

或手动执行：

```powershell
cd /d D:\MouseTranslatorPro
python -m pip install -r requirements.txt
python -m PyInstaller mouse_translator.spec --clean --noconfirm
```

打包结果：

```text
dist\MouseTranslatorPro\MouseTranslatorPro.exe
```

如果 OCR 或翻译 provider 在打包后缺少运行时组件，请确认相关包已经安装在打包使用的 Python 环境中。Tesseract OCR 是系统外部程序，不会被 PyInstaller 自动打包，需要用户单独安装并配置 `PATH`。

## 隐私说明

- 本软件通过模拟 `Ctrl+C` 获取用户当前选中的文本。
- 如果使用 Google、DeepL 或 OpenAI 翻译，选中文本会发送给对应翻译服务。
- 软件本身不保存完整选中文本。
- 日志只记录程序启动、退出、错误、provider 错误和文本长度，不记录正文。
- API Key 只从环境变量读取，不写死在源码中，也不会写入日志。

## 已知限制

- 第一版仅支持 Windows。
- 获取选中文本依赖目标软件对 `Ctrl+C` 的支持；部分安全软件、游戏、远程桌面或特殊控件可能无法复制选区。
- `pyperclip` 只能可靠恢复文本剪贴板；如果原剪贴板是图片或复杂格式，可能无法完整恢复。
- `google` provider 依赖 `deep-translator` 和网络环境，可能受第三方服务变化影响。
- OCR 准确率取决于截图质量、字体、语言包和系统 Tesseract 安装情况。

## 常见问题

### 为什么没有弹窗？

请确认程序托盘状态为启用，目标软件选中文本后可以手动 `Ctrl+C` 复制，且文本长度不小于 `min_text_length`。

### 为什么连续选同一段不重复弹窗？

程序有 `debounce_ms` 防抖逻辑，避免同一段文本在短时间内反复刷屏。

### OpenAI 或 DeepL 没有 key 会怎样？

程序会在弹窗里显示明确错误，例如缺少 `OPENAI_API_KEY` 或 `DEEPL_API_KEY`，主程序不会退出。

### OCR 为什么提示安装？

OCR 需要 Python 包 `pytesseract`、`pillow` 和系统 Tesseract OCR 程序。缺少任何关键组件都会提示安装方式。

### 是否需要管理员权限？

第一版不要求管理员权限。全局鼠标监听和快捷键使用 `pynput`，不使用键盘记录器，也不保存完整用户文本。
