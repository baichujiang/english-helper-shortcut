# Privacy / 隐私说明

## 当前分发版 v1.1

- 手动启动后读取一次剪贴板快照，处理复制的那段文字。
- 模型动作固定为 `Apple Intelligence on Device`。项目不调用自建服务、第三方 API 或其他快捷指令。
- 结果先预览，只有确认后才写入手机本地剪贴板。取消与输入保护分支不执行复制。
- 没有账号、遥测、分析统计、广告、文本历史或持久化日志功能。
- 源码与签名包可独立核对，参见 `scripts/verify_signed.py`；它校验包内实际动作，而不仅是文件名。

设备端模型由 Apple 系统提供和管理。模型准备、系统设置及 Apple 软件本身的数据处理遵循 Apple 的政策；本项目的说明不替代这些政策。不要把后续自行改为云模型或添加网络动作的版本视为同一隐私配置。

本地剪贴板仍属于系统剪贴板。其他复制操作以及通用剪贴板可能更新其内容；预览中显示的“原文”是本次处理的实际输入。使用后清理剪贴板由用户自己决定，项目不会后台监听它。

## 验收和反馈

`qa/` 和验收工具只使用合成例句。临时网页的复制与编辑在浏览器本地执行，没有提交文本的接口。开发用 HTTP 服务器可能记录访问路径和连接地址，未加入项目的运行时目录不作为发布内容。

提交 Issue 时，请使用合成文本，删除真实聊天、账号、设备标识及截图中的私人信息。项目不需要你的 API 密钥、密码或 Apple 账户信息。

## English

The distributed v1.1 workflow reads a clipboard snapshot only when manually started. It explicitly selects Apple's on-device model and copies the replacement only after confirmation. This project has no backend, third-party API calls, analytics, accounts, text history, or persistent text logs.

Apple manages the system model and its availability under Apple's policies. The system clipboard can change through other copy operations or Universal Clipboard; the displayed original is the actual input. Changing the model or adding network actions changes the privacy properties of a fork.

QA uses synthetic text. The local test page does not submit edited text. Development HTTP servers can log request paths and connection addresses; runtime files are excluded from releases. Use synthetic examples in public reports and omit private screenshots, credentials, and device identifiers.
