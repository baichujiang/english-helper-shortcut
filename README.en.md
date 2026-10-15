# English Helper

[简体中文](README.md) · [Download](https://github.com/baichujiang/english-helper-shortcut/releases/latest) · [Roadmap](ROADMAP.md) · [MIT](LICENSE)

Proofread or polish English on iPhone while keeping your existing keyboard. Copy text in your current app, tap AssistiveTouch, preview the edit, confirm, and paste it into the original field.

**Stable version: v1.1.** This is an Apple Shortcuts workflow using the on-device Apple Intelligence model. No API key or project backend is required. The shortcut interface currently uses Simplified Chinese; the text it edits is English.

## Install and use

1. On iPhone, download `English-Helper-v1.1.zip` from the [release page](https://github.com/baichujiang/english-helper-shortcut/releases/latest). Tap the ZIP in Files to extract `英文助手 v1.1.shortcut`; the ZIP preserves its Chinese filename.
2. Open the extracted `.shortcut` file and add the shortcut. The individual [signed file](dist/英文助手%20v1.1.shortcut) is also available in the repository. AirDrop from a Mac is another installation route.
3. In **Settings → Accessibility → Touch → AssistiveTouch**, enable AssistiveTouch and set **Single-Tap** to **英文助手 v1.1**.
4. Copy English in your current app and tap AssistiveTouch.
5. Choose **检查：只改错误** (minimal grammar, spelling, and punctuation fixes) or **润色：更自然** (optional natural wording).
6. Compare the original and edit. **好** confirms copying; **取消** cancels. Select the original text in your app and paste.

The system may ask for permission to copy the result on first use. Example: `She don't like coffee.` → `She doesn't like coffee.`

## Requirements and limits

You need an Apple Intelligence-enabled iPhone with the on-device **Use Model** action available in Shortcuts. The tested environment is iPhone 16 Pro Max with iOS 26.0.1. Other configurations have not been individually verified. Check Apple's [availability requirements](https://support.apple.com/en-us/121115) and [model action guide](https://support.apple.com/guide/shortcuts/use-apple-intelligence-in-shortcuts-tpg3vrvwmclv/ios).

- Up to 1500 characters per run. One paragraph at a time is recommended; line breaks may be merged.
- AI can miss mistakes or change meaning. Review the actual edit before accepting it.
- Copying and pasting remain manual, and some apps restrict them.
- The workflow reads a clipboard snapshot at launch. Universal Clipboard can replace iPhone clipboard contents when you copy something on a Mac; check the original text displayed.
- Word-level highlighting, grammar explanations, automatic replacement, Share Sheet support, and background monitoring are not included.

The original user reports the current version is usable. The [validation record](evidence/v1-validation.md) distinguishes device observations, user reports, Mac checks, and untested cases. It is not a claim of universal compatibility.

## Privacy and development

The workflow reads the clipboard only when started manually, selects the on-device model, and copies an edit only after confirmation. The project has no backend, analytics, accounts, or text history. See [Privacy](PRIVACY.md).

Python 3.11+ is required. Source generation and static checks work without a Mac; signing and archive verification require macOS with Apple's Shortcuts and archive tools.

```sh
python3 scripts/validate_sources.py
python3 -m unittest discover -s tests -v
python3 scripts/build_shortcuts.py
# macOS, for installable signed files:
python3 scripts/build_shortcuts.py --sign
python3 scripts/verify_signed.py
```

Edit the generator and prompts in `scripts/build_shortcuts.py`, then regenerate `shortcuts/`. The manifest records source/package hashes. Signed binaries need not be byte-for-byte reproducible; verification compares their actual workflow contents to the source. Signing does not replace device testing.

[Contributing](CONTRIBUTING.md) · [Architecture](docs/architecture.md) · [Changelog](CHANGELOG.md)

MIT covers this repository's code, prompts, workflows, and documentation. Apple Shortcuts and the Apple Intelligence model are not distributed here and remain subject to Apple's terms. This is an independent community project.
