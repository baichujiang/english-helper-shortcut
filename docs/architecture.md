# 工作原理 / Architecture

```text
读取剪贴板 → 生成原文快照 → 检查空白/1500字符/英文字母
  → 选择检查或润色 → 设备端模型生成全文
  → 检查结果非空 → 比较中文字符序列
  → 无修改时显示实际原文并停止
  → 原文与修改版预览 → 确认复制 → 提示手动粘贴
```

`scripts/build_shortcuts.py` 是主源码。`english_helper()` 返回工作流字典，包含标准动作、提示词和变量引用。它可以被其他 Python 构建工具导入复用；当前没有独立 iOS SDK 或原生 App。

动作 UUID 由稳定标签生成，文本附件位置按 UTF-16 计算，适配快捷指令的序列化格式。`shortcuts/EnglishHelper.plist` 保存完整可审查的 XML；签名输入另以二进制 plist 生成到 `build/unsigned/`。

设备端模型依靠提示词区分“尽量少改”的检查和“更自然”的润色。中文一致性只比较 Han 字符序列，不能保证标点、链接、数字、名称或换行均不变化。这些是当前限制，后续保护见路线图。

工作流只含一个写入剪贴板动作，紧跟可取消的预览确认框，并绑定实际生成的修改版。源码校验、安装包真实性校验与模型/交互真机验收是三种不同证据，互相不能替代。

分发 `.shortcut` 文件由 Apple 的签名工具处理；签名工具会移除文件名派生的名称、更新客户端构建号。签名验证脚本仅忽略这两个元数据差异，逐值核对其余工作流内容，并记录 SHA-256。

The generator returns a standard Shortcuts workflow dictionary. Stable action IDs and UTF-16 token ranges connect the actions. The workflow takes one input snapshot, uses the on-device model, validates the result, and gates its sole clipboard write behind explicit preview confirmation.

The Han-character guard is limited: it does not prove preservation of punctuation, names, numbers, URLs, or formatting. Static workflow validation, cryptographic package verification, and device/model QA serve separate purposes.
