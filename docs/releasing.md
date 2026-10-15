# 发布流程 / Releasing

1. 使用合成文本完成真机验收，将设备、系统、入口和结果写入 `evidence/`。记录未覆盖的场景。
2. 更新 `PRODUCT_NAME`、更新记录、安装说明和绑定名称；功能变化必须重新验收。
3. 在 Mac 上构建并验证：

   ```sh
   python3 scripts/build_shortcuts.py --sign
   python3 scripts/verify_signed.py
   python3 scripts/validate_sources.py
   python3 -m unittest discover -s tests -v
   ```

4. 仅提交源码、签名包和公开文档；`build/`、私人截图、剪贴板内容和本机路径不加入仓库。
5. 为已检查的提交创建版本标签。GitHub Release 附带正式版 `.shortcut`、`manifest.json` 和对应 SHA-256 清单。探针是开发工具，不作为普通用户的主安装入口。
6. 核对公开下载后的文件哈希，确认 README 的链接、版本和辅助触控绑定说明一致。

签名需要本机 Apple 工具及其正常可用的签名环境，不在 CI 中自动登录 Apple 账户。签名可能包含分发所需的公开签名元数据；没有 Apple 模型权重、账号凭据或私钥随项目发布。

源码校验和 GitHub Actions 通过不代表模型效果或跨 App 体验已通过。发布说明应保留实际设备覆盖范围。

Build and sign on macOS, verify archive contents, run the validator and regression tests, then tag the reviewed commit. Release the main signed shortcut with its manifest and checksums. Do not include runtime directories, real text, private screenshots, credentials, or local paths. Recheck downloaded assets and keep device QA distinct from CI results.
