# English Helper · 英文助手

[English](README.en.md) · [下载安装包](https://github.com/baichujiang/english-helper-shortcut/releases/latest) · [优化路线](ROADMAP.md) · [MIT 许可](LICENSE)

保留现有键盘，在原 App 复制英文，点辅助触控“小白点”，检查语法或选择润色；预览并确认后，粘贴回原输入框。

**当前稳定版：v1.1。** 这是使用 Apple 智能设备端模型的快捷指令项目。无需 API 密钥，无需自建服务器。界面目前为简体中文，处理内容为英文。

```text
原 App 复制英文 → 小白点 → 检查 / 润色 → 原文与修改版 → 确认复制 → 原框粘贴
```

## 功能

- **检查**：尽量少改，修正英文语法、拼写和标点。
- **可选润色**：让表达更自然，要求保留原意和语气。
- 采用前展示原文与修改版；取消不会执行复制。
- 没有修改建议时也显示实际读取的原文，便于发现剪贴板未更新。
- 拦截空白、没有英文字母和超过1500字符的输入；结果改动中文时停止。

## 安装

1. 在 iPhone 打开[发布页](https://github.com/baichujiang/english-helper-shortcut/releases/latest)，下载 `English-Helper-v1.1.zip`。在“文件”App 中轻点 ZIP 解压，得到 `英文助手 v1.1.shortcut`。ZIP 会保留正确的中文文件名。
2. 打开解压得到的 `.shortcut` 文件，选择“添加快捷指令”。也可从仓库的 [dist](dist/英文助手%20v1.1.shortcut) 下载单个签名文件，或将文件从 Mac 隔空投送到 iPhone 后安装。
3. 打开“设置 → 辅助功能 → 触控 → 辅助触控”，开启辅助触控。
4. 在“轻点一下”中选择 **英文助手 v1.1**。安装新版后，请核对绑定的版本名称。

首次复制结果时，系统可能询问是否允许拷贝到剪贴板。完成安装和绑定后，日常检查流程在原 App 中进行。

## 使用

1. 在原输入框选中并复制需要处理的英文。
2. 点小白点，选择“检查：只改错误”或“润色：更自然”。
3. 核对原文和修改版，点“好”复制修改版；点“取消”保留原剪贴板。
4. 在原输入框选中需要替换的文字，再粘贴。

示例：`She don't like coffee.` → `She doesn't like coffee.`

它处理的是运行时的剪贴板快照。Mac 的通用剪贴板可能更新手机剪贴板；如果显示的原文不对，请重新复制后再运行。

## 设备要求与边界

- 需要支持并已启用 Apple 智能的 iPhone，以及快捷指令中的设备端“使用模型”动作。已验证环境为 **iPhone 16 Pro Max / iOS 26.0.1**；其他组合尚未逐一验证。
- Apple 智能受设备、语言和地区可用性限制。请查看 [Apple 官方要求](https://support.apple.com/en-us/121115)及[快捷指令模型说明](https://support.apple.com/guide/shortcuts/use-apple-intelligence-in-shortcuts-tpg3vrvwmclv/ios)。
- 每次最多1500字符，建议按段处理。模型可能合并换行，也可能漏检或改偏；请预览后采用。
- 仍需手动复制、选择和粘贴；部分 App 会限制这些操作。
- 当前提供原文与修改版对照；逐词高亮、中文修改理由、共享表单、自动替换和持续监测均未包含。

用户已确认当前版本可用。检查、润色、取消、确认复制等单项有真机或 Mac 实测记录；仍未覆盖的边界场景明确列在[验收记录](evidence/v1-validation.md)，不把一台设备的结果视为全部 App 的兼容保证。

## 隐私

工作流仅在手动启动时读取剪贴板，固定选择设备端模型，确认后才写入本地剪贴板。本项目没有服务器、账号系统、分析统计或文本历史记录。[详细说明](PRIVACY.md)

## 开发与复现

Python 3.11+；生成源码与静态校验可在任意支持 Python 的系统运行。签名和签名内容校验需要 macOS 的 `shortcuts`、`aea`、`aa` 和 `openssl` 工具；签名由 Apple 的快捷指令工具完成。

```sh
python3 scripts/validate_sources.py
python3 -m unittest discover -s tests -v

# 修改生成器后，重新生成可审查的 XML 源码
python3 scripts/build_shortcuts.py

# 在 Mac 上构建可安装包并验证实际内容
python3 scripts/build_shortcuts.py --sign
python3 scripts/verify_signed.py
```

源码生成可重复；Apple 签名后的文件不保证逐字节可重复。`dist/manifest.json` 记录源码和分发包的 SHA-256，签名校验会核对实际工作流内容。签名成功与真机功能验收分别记录。

| 路径 | 内容 |
| --- | --- |
| `scripts/build_shortcuts.py` | 工作流生成器和提示词，修改从这里开始 |
| `shortcuts/EnglishHelper.plist` | 可审查的正式版工作流 |
| `dist/` | 签名安装包和哈希清单；普通用户只需正式版 |
| `scripts/validate_sources.py` | 源码、变量、控制流和复制确认校验 |
| `qa/iphone-smoke.html` | 仅含合成文本的开发验收页 |
| `evidence/` | 区分用户反馈、真机观察与 Mac 测试的记录 |

另外三个带“探针”名称的工作流用于独立验证入口、剪贴板或模型，不代替正式版。开发验收工具通过 `python3 scripts/build_qa.py` 生成在被忽略的 `build/qa/`，会明确提示覆盖剪贴板为合成样例。[贡献指南](CONTRIBUTING.md) · [真机验收步骤](docs/iPhone验收.md) · [架构](docs/architecture.md)

## 许可

本仓库代码、提示词、工作流和文档采用 [MIT License](LICENSE)。Apple 快捷指令和 Apple 智能模型不随本仓库分发，其使用遵循 Apple 的条款。本项目为独立社区项目。
