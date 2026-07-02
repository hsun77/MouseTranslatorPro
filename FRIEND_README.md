# MouseTranslatorPro 朋友版快速使用

## 直接启动

解压整个文件夹后，双击：

```text
启动 MouseTranslatorPro.bat
```

或直接双击：

```text
MouseTranslatorPro.exe
```

启动后程序会进入系统托盘。右键托盘图标可以打开设置、暂停/恢复、测试翻译或退出。

## 默认翻译

默认 provider 是：

```text
google
```

这种方式通常不需要 API Key。如果网络环境导致 Google 翻译不可用，可以在托盘菜单里打开设置，把 provider 改成 `youdao` 或 `tencent`。

## 切换到有道

1. 开通有道智云文本翻译服务。
2. 在 Windows PowerShell 中设置环境变量：

```powershell
[Environment]::SetEnvironmentVariable("YOUDAO_APP_KEY", "你的应用 ID", "User")
[Environment]::SetEnvironmentVariable("YOUDAO_APP_SECRET", "你的应用密钥", "User")
```

3. 重新启动 MouseTranslatorPro。
4. 托盘菜单打开设置，把翻译服务改成 `youdao` 并保存。

## 切换到腾讯翻译

1. 开通腾讯云机器翻译 TMT 服务。
2. 在 Windows PowerShell 中设置环境变量：

```powershell
[Environment]::SetEnvironmentVariable("TENCENTCLOUD_SECRET_ID", "你的 SecretId", "User")
[Environment]::SetEnvironmentVariable("TENCENTCLOUD_SECRET_KEY", "你的 SecretKey", "User")
```

3. 重新启动 MouseTranslatorPro。
4. 托盘菜单打开设置，把翻译服务改成 `tencent` 并保存。

## 快捷键

- `Ctrl+Alt+T`：启用/暂停划词翻译。
- `Ctrl+Alt+C`：翻译当前剪贴板内容。
- `Ctrl+Alt+Q`：退出程序。
- `Ctrl+Alt+O`：OCR 截图翻译入口，OCR 需要额外安装 Tesseract。

## 隐私提醒

- 软件通过模拟 `Ctrl+C` 获取当前选中的文本。
- 使用 Google、有道或腾讯翻译时，选中文本会发送给对应翻译服务。
- 软件本身不保存完整选中文本。
- 日志只记录错误和文本长度，不记录正文。
