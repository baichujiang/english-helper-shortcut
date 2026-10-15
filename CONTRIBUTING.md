# Contributing / 贡献指南

欢迎反馈兼容性、提交合成语法用例、改进提示词和安装说明。

## 修改与验证

1. 修改 `scripts/build_shortcuts.py` 中的生成器。`shortcuts/*.plist` 是可审查的生成结果，避免只手动改生成文件。
2. 运行 `python3 scripts/build_shortcuts.py` 重新生成源码。
3. 运行 `python3 scripts/validate_sources.py` 和 `python3 -m unittest discover -s tests -v`。
4. 发布安装文件时，在 Mac 上运行 `python3 scripts/build_shortcuts.py --sign`，然后运行 `python3 scripts/verify_signed.py`。
5. 按 `docs/iPhone验收.md` 做真机验收。模型质量、复制粘贴及小白点入口必须与静态校验分别记录。

只生成源码会使旧安装包的内容校验状态失效；发布前必须重新签名和验证。CI 不需要 Apple 账户，不会替你签名或运行设备端模型。

## 需要保持的行为

- 手动读取剪贴板，模型默认固定设备端。
- 先预览，确认后复制。取消、失败和校验不通过时保留剪贴板。
- 分享的安装包、生成源码、版本说明与哈希一致。
- 新增模型、网络请求或不同权限时，明确说明变化并重新验收。

## 报告问题

请提供系统版本、设备型号、发生问题的 App、出问题的步骤、合成输入及实际结果。注明是从小白点还是资料库运行；粘贴问题请核对原文是否是刚复制的内容。截图中删除私人内容，不提交真实聊天或密钥。

## English

Edit the generator, regenerate the XML workflows, then run the source validator and unit tests. Installable releases also need Apple signing, archive-content verification, and physical-device QA. CI neither needs an Apple account nor invokes the model.

Preserve manual activation, the on-device default, preview-before-copy, and cancellation without a clipboard write. Report model/network/permission changes explicitly. Use synthetic examples in issues, and distinguish AssistiveTouch, library, Mac, and on-device results.
