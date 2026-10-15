#!/usr/bin/env python3
"""Build the English helper and its separate verification probes.

The workflow container and menu format follow Apple's bundled Gallery .wflow
examples. Only standard Shortcuts actions are used. Signing uses Apple's
`shortcuts sign` command; no private frameworks are linked or executed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import subprocess
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTION_PREFIX = "is.workflow.actions."
PRODUCT_NAME = "英文助手 v1.1"
TEST_RESULT = "She doesn't like coffee."


def identifier(label: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"english-helper/probe/v1/{label}")).upper()


def action(name: str, **parameters: object) -> dict:
    return {
        "WFWorkflowActionIdentifier": ACTION_PREFIX + name,
        "WFWorkflowActionParameters": parameters,
    }


def output(label: str, name: str) -> dict:
    return {"Type": "ActionOutput", "OutputUUID": identifier(label), "OutputName": name}


def attachment(value: dict) -> dict:
    return {"Value": value, "WFSerializationType": "WFTextTokenAttachment"}


def text_token(prefix: str, value: dict, suffix: str = "") -> dict:
    # Shortcuts uses UTF-16 offsets, including for non-BMP emoji.
    offset = len(prefix.encode("utf-16-le")) // 2
    return {
        "Value": {
            "string": prefix + "\ufffc" + suffix,
            "attachmentsByRange": {f"{{{offset}, 1}}": value},
        },
        "WFSerializationType": "WFTextTokenString",
    }


def text_parts(*parts: str | dict) -> dict:
    text = ""
    ranges = {}
    for part in parts:
        if isinstance(part, str):
            text += part
        else:
            ranges[f"{{{len(text.encode('utf-16-le')) // 2}, 1}}"] = part
            text += "\ufffc"
    return {"Value": {"string": text, "attachmentsByRange": ranges},
            "WFSerializationType": "WFTextTokenString"}


def condition(label: str, value: dict, code: int, **literal: object) -> dict:
    return action("conditional", WFControlFlowMode=0,
                  GroupingIdentifier=identifier(label), WFCondition=code,
                  WFInput={"Type": "Variable", "Variable": attachment(value)}, **literal)


def end_condition(label: str, result: str | None = None) -> dict:
    params = {"WFControlFlowMode": 2, "GroupingIdentifier": identifier(label)}
    if result:
        params["UUID"] = identifier(result)
    return action("conditional", **params)


def reject_if_empty(label: str, value: dict, message: str) -> list[dict]:
    return [condition(label, value, 101),
            action("alert", WFAlertActionTitle="英文助手", WFAlertActionMessage=message,
                   WFAlertActionCancelButtonShown=False),
            action("exit"), end_condition(label)]


def workflow(name: str, actions: list[dict], *, share: bool = False) -> dict:
    return {
        "WFWorkflowName": name,
        "WFWorkflowClientVersion": "4033.0.3.5",
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowMinimumClientVersionString": "900",
        "WFWorkflowIcon": {
            "WFWorkflowIconStartColor": 463140863,
            "WFWorkflowIconGlyphNumber": 61592,
        },
        "WFWorkflowActions": actions,
        "WFWorkflowTypes": ["ActionExtension"] if share else [],
        "WFQuickActionSurfaces": [],
        "WFWorkflowInputContentItemClasses": ["WFStringContentItem", "WFRichTextContentItem"],
        "WFWorkflowOutputContentItemClasses": [],
        "WFWorkflowHasOutputFallback": False,
        "WFWorkflowHasShortcutInputVariables": share,
        **({"WFWorkflowNoInputBehavior": {
            "Name": "WFWorkflowNoInputBehaviorGetClipboard", "Parameters": {},
        }} if share else {}),
        "WFWorkflowImportQuestions": [],
    }


def smoke_probe() -> dict:
    return workflow(
        "英文助手·入口探针",
        [
            action(
                "comment",
                WFCommentActionText=(
                    "离线入口验证。只显示一个系统弹窗，不读取剪贴板、不联网、"
                    "不调用其他 App。请从辅助触控小白点运行，不要从快捷指令 App 运行。"
                ),
            ),
            action(
                "alert",
                WFAlertActionTitle="英文助手：入口验证",
                WFAlertActionMessage=(
                    "请检查弹窗后面是否仍是刚才的 App。\n\n"
                    "关闭弹窗后，应该直接继续在原 App 操作。\n\n"
                    "若出现快捷指令 App 主界面，或需要手动切回原 App，入口验证不通过。\n\n"
                    "此探针完全离线，不执行语法检查。"
                ),
                WFAlertActionCancelButtonShown=False,
            ),
        ],
    )


def clipboard_probe() -> dict:
    menu_id = identifier("mode-menu")
    steps = [
        action(
            "comment",
            WFCommentActionText=(
                "离线固定示例，只验证界面和剪贴板流程，尚未实现语法检查或润色。"
                "请先复制 She don't like coffee.，再从小白点启动。"
                "只有确认复制后才覆盖剪贴板。"
            ),
        ),
        action("getclipboard", UUID=identifier("clipboard")),
        action(
            "choosefrommenu",
            WFMenuPrompt="英文助手 · 离线入口验证",
            WFMenuItems=["检查入口（固定示例）", "润色入口（固定示例）"],
            WFControlFlowMode=0,
            GroupingIdentifier=menu_id,
        ),
    ]
    for label in ["检查入口（固定示例）", "润色入口（固定示例）"]:
        steps.extend(
            [
                action(
                    "choosefrommenu",
                    WFMenuItemTitle=label,
                    WFControlFlowMode=1,
                    GroupingIdentifier=menu_id,
                ),
                action("gettext", WFTextActionText=TEST_RESULT),
            ]
        )
    steps.extend(
        [
            action(
                "choosefrommenu",
                WFControlFlowMode=2,
                GroupingIdentifier=menu_id,
                UUID=identifier("mode-result"),
            ),
            action(
                "alert",
                WFAlertActionTitle="确认复制固定测试结果？",
                WFAlertActionMessage=text_token(
                    "刚才复制的内容：\n",
                    output("clipboard", "Clipboard"),
                    "\n\n固定测试结果（与输入内容无关）：\n"
                    + TEST_RESULT
                    + "\n\n这里只验证流程，尚未接入校对功能。"
                    "\n点“好”才会将固定测试结果写入剪贴板；点“取消”保留原剪贴板。",
                ),
                WFAlertActionCancelButtonShown=True,
            ),
            action(
                "setclipboard",
                WFInput=attachment(output("mode-result", "Menu Result")),
                WFLocalOnly=True,
            ),
            action(
                "alert",
                WFAlertActionTitle="固定测试结果已复制",
                WFAlertActionMessage=(
                    "关闭弹窗后，应该直接回到刚才的 App。\n\n"
                    "在原输入框选中测试句，再粘贴。\n\n"
                    "预期：She doesn't like coffee.\n\n"
                    "请确认过程中没有进入快捷指令 App 主界面。"
                ),
                WFAlertActionCancelButtonShown=False,
            ),
        ]
    )
    return workflow("英文助手·剪贴板探针", steps)


def model_probe() -> dict:
    return workflow("英文助手·模型验证", [
        action("comment", WFCommentActionText="仅用固定测试句验证设备端模型，不读取或写入剪贴板。"),
        action("askllm", WFLLMModel="Apple Intelligence on Device",
               WFLLMPrompt=("Correct the grammar of this sentence. Return only the corrected sentence, "
                            "without quotes or explanations: She don't like coffee."),
               WFGenerativeResultType="Text", UUID=identifier("model-probe")),
        action("showresult", Text=text_token("设备端模型实际结果：\n", output("model-probe", "Response"))),
    ])


def english_helper() -> dict:
    original = output("helper-original", "原文")
    replacement = output("helper-replacement", "修改版")
    mode_id = identifier("helper-mode")
    steps = [
        action("comment", WFCommentActionText=(
            PRODUCT_NAME + "。复制英文后从辅助触控启动。"
            "设备端 Apple 智能处理，不调用其他 App。预览后确认才复制。取消和错误不会改动剪贴板。"
            "建议每次处理短消息，最多1500字符；采用前请对照原文核对修改版。")),
        action("getclipboard", UUID=identifier("helper-clipboard")),
        action("gettext", WFTextActionText=text_parts(output("helper-clipboard", "Clipboard")),
               UUID=identifier("helper-original")),
        action("text.match", WFMatchTextPattern=r"\S", text=text_parts(original),
               UUID=identifier("helper-nonempty")),
    ]
    steps += reject_if_empty("helper-empty", output("helper-nonempty", "Matches"),
                             "请先在当前 App 选中并复制要检查的英文，再点小白点。剪贴板未改动。")
    steps += [action("text.match", WFMatchTextPattern=r"(?s)\A.{1,1500}\z",
                     text=text_parts(original), UUID=identifier("helper-length"))]
    steps += reject_if_empty("helper-too-long", output("helper-length", "Matches"),
                             "这段文字超过1500字符。请分段复制后重试；剪贴板未改动。")
    steps += [action("text.match", WFMatchTextPattern="[A-Za-z]", text=text_parts(original),
                     UUID=identifier("helper-english"))]
    steps += reject_if_empty("helper-no-english", output("helper-english", "Matches"),
                             "没有找到英文字母。请复制含英文的文字后重试；剪贴板未改动。")
    steps += [action("choosefrommenu", WFMenuPrompt="英文助手 · 请选择",
                     WFMenuItems=["检查：只改错误", "润色：更自然"],
                     WFControlFlowMode=0, GroupingIdentifier=mode_id)]
    for title, instruction in [
        ("检查：只改错误", "Correct only the English grammar, spelling, and punctuation in the text below. "
         "Make the smallest necessary edits. Do not rewrite correct wording."),
        ("润色：更自然", "Polish the English in the text below to sound natural and fluent. "
         "Keep its original tone and level of formality."),
    ]:
        steps += [action("choosefrommenu", WFMenuItemTitle=title, WFControlFlowMode=1,
                         GroupingIdentifier=mode_id), action("gettext", WFTextActionText=instruction)]
    steps += [action("choosefrommenu", WFControlFlowMode=2, GroupingIdentifier=mode_id,
                     UUID=identifier("helper-instruction")),
              action("askllm", WFLLMModel="Apple Intelligence on Device",
                     WFGenerativeResultType="Text", UUID=identifier("helper-response"),
                     WFLLMPrompt=text_parts(
                         output("helper-instruction", "Editing mode"),
                         " Keep English in English. Do not translate into Chinese or any other language. "
                         "Preserve its meaning. Keep Chinese text, names, numbers, URLs, emoji, "
                         "and line breaks unchanged. Return only the complete edited text, without "
                         "explanations or quotation marks. If no changes are needed, repeat it unchanged."
                         "\n\nText to edit:\n", original)),
              action("gettext", WFTextActionText=text_parts(output("helper-response", "Response")),
                     UUID=identifier("helper-replacement")),
              action("text.match", WFMatchTextPattern=r"\S", text=text_parts(replacement),
                     UUID=identifier("helper-valid-result"))]
    steps += reject_if_empty("helper-invalid", output("helper-valid-result", "Matches"),
                             "这次没有得到有效修改版，请重试。剪贴板未改动。")
    # Device-side models can translate mixed-language input despite instructions.
    # Compare the actual Han characters before permitting any clipboard write.
    for label, value in [("original", original), ("replacement", replacement)]:
        steps += [action("text.match", WFMatchTextPattern=r"\p{Han}", text=text_parts(value),
                         UUID=identifier(f"helper-han-{label}")),
                  action("gettext", WFTextActionText=text_parts("Han:", output(f"helper-han-{label}", "Matches")),
                         UUID=identifier(f"helper-han-text-{label}"))]
    steps += [condition("helper-language-changed", output("helper-han-text-original", "原文中文"), 5,
                        WFConditionalActionString=text_parts(output("helper-han-text-replacement", "结果中文"))),
              action("alert", WFAlertActionTitle="这次结果改动了中文，已停止",
                     WFAlertActionMessage="请只选中英文部分复制后重试。剪贴板保持原样。",
                     WFAlertActionCancelButtonShown=False), action("exit"),
              end_condition("helper-language-changed")]
    steps += [condition("helper-unchanged", replacement, 4,
                        WFConditionalActionString=text_parts(original)),
              action("alert", WFAlertActionTitle="本次没有修改建议",
                     WFAlertActionMessage=text_parts(
                         "本次检查的原文\n", original,
                         "\n\n剪贴板保持原样。若上面不是你刚复制的文字，请重新选中并复制后再检查。"),
                     WFAlertActionCancelButtonShown=False), action("exit"),
              end_condition("helper-unchanged"),
              action("alert", WFAlertActionTitle="确认复制这份修改？",
                     WFAlertActionMessage=text_parts(
                         "原文\n", original, "\n\n修改版\n", replacement,
                         "\n\n点“好”复制修改版；点“取消”保留剪贴板。"),
                     WFAlertActionCancelButtonShown=True),
              action("setclipboard", WFInput=attachment(replacement), WFLocalOnly=True),
              action("alert", WFAlertActionTitle="修改版已复制",
                     WFAlertActionMessage="在原输入框选中需要替换的原文，再点粘贴。",
                     WFAlertActionCancelButtonShown=False), action("nothing")]
    return workflow(PRODUCT_NAME, steps)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sign", action="store_true", help="Sign installable files using Apple's CLI")
    parser.add_argument("--only", choices=["EntryProbe", "ClipboardProbe", "ModelProbe", "EnglishHelper"],
                        help="Limit signing to one workflow; all reviewable sources are generated")
    args = parser.parse_args()
    source_dir = ROOT / "shortcuts"
    dist_dir = ROOT / "dist"
    unsigned_dir = ROOT / "build" / "unsigned"
    source_dir.mkdir(exist_ok=True)
    dist_dir.mkdir(exist_ok=True)
    unsigned_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = dist_dir / "manifest.json"
    previous = {entry["file"]: entry for entry in json.loads(manifest_path.read_text())} if manifest_path.exists() else {}
    manifest = []
    workflows = [("EntryProbe", smoke_probe()), ("ClipboardProbe", clipboard_probe()),
                 ("ModelProbe", model_probe()), ("EnglishHelper", english_helper())]
    for slug, data in workflows:
        source = source_dir / f"{slug}.plist"
        source.write_bytes(plistlib.dumps(data, fmt=plistlib.FMT_XML, sort_keys=False))
        unsigned = unsigned_dir / f"{slug}.shortcut"
        unsigned.write_bytes(plistlib.dumps(data, fmt=plistlib.FMT_BINARY, sort_keys=False))
        signed = dist_dir / f"{data['WFWorkflowName']}.shortcut"
        signed_now = args.sign and (not args.only or slug == args.only)
        if signed_now:
            subprocess.run(
                ["shortcuts", "sign", "--mode", "anyone", "--input", str(unsigned), "--output", str(signed)],
                check=True,
            )
        source_digest = hashlib.sha256(source.read_bytes()).hexdigest()
        file_digest = hashlib.sha256(signed.read_bytes()).hexdigest() if signed.exists() else None
        old = previous.get(str(signed.relative_to(ROOT)), {})
        if signed_now:
            status = "signed-awaiting-content-verification"
        elif file_digest is None:
            status = "source-only"
        elif (old.get("source_sha256") == source_digest
              and old.get("file_sha256") == file_digest
              and old.get("status") == "signature-and-content-verified-see-runtime-evidence"):
            status = old["status"]
        else:
            status = "package-needs-content-verification"
        manifest.append(
            {
                "name": data["WFWorkflowName"],
                "source": str(source.relative_to(ROOT)),
                "file": str(signed.relative_to(ROOT)),
                "actions": len(data["WFWorkflowActions"]),
                "source_sha256": source_digest,
                "file_sha256": file_digest,
                "status": status,
            }
        )
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
