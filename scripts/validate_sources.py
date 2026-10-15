#!/usr/bin/env python3
"""Validate generated workflows and clipboard/privacy contracts without a device.

This does not execute the model or authenticate signed archives. On macOS, also
run verify_signed.py; interaction and model quality require physical-device QA.
"""
from __future__ import annotations

import hashlib
import json
import plistlib
import re
from pathlib import Path

from build_shortcuts import (
    ROOT, ACTION_PREFIX, clipboard_probe, english_helper, identifier,
    model_probe, smoke_probe,
)


def require(value: object, message: str) -> None:
    if not value:
        raise ValueError(message)


def walk(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def validate_workflow(data: dict, *, product: bool = False) -> None:
    seen: set[str] = set()
    groups: list[tuple[str, str]] = []
    actions = data['WFWorkflowActions']
    for index, step in enumerate(actions):
        kind = step['WFWorkflowActionIdentifier']
        params = step['WFWorkflowActionParameters']
        for item in walk(params):
            if not isinstance(item, dict):
                continue
            if 'OutputUUID' in item:
                require(item['OutputUUID'] in seen, f'Action {index}: unknown/forward output reference')
            if item.get('WFSerializationType') == 'WFTextTokenString':
                token = item['Value']
                encoded = token['string'].encode('utf-16-le')
                positions: set[int] = set()
                for span in token.get('attachmentsByRange', {}):
                    match = re.fullmatch(r'\{(\d+), (\d+)\}', span)
                    require(match is not None, f'Action {index}: malformed token range')
                    offset, length = map(int, match.groups())
                    require(length == 1 and offset not in positions,
                            f'Action {index}: invalid/duplicate token range')
                    require(encoded[2 * offset:2 * (offset + length)] == '\ufffc'.encode('utf-16-le'),
                            f'Action {index}: token range is not a UTF-16 attachment position')
                    positions.add(offset)
                require(len(positions) == token['string'].count('\ufffc'),
                        f'Action {index}: unbound text attachment')
        if kind in {ACTION_PREFIX + 'conditional', ACTION_PREFIX + 'choosefrommenu'}:
            mode, group = params['WFControlFlowMode'], params['GroupingIdentifier']
            if mode == 0:
                groups.append((kind, group))
            else:
                require(bool(groups) and groups[-1] == (kind, group),
                        f'Action {index}: mismatched control flow group')
                require(mode in (1, 2), f'Action {index}: invalid control flow mode')
                if mode == 2:
                    groups.pop()
        if 'UUID' in params:
            require(params['UUID'] not in seen, f'Action {index}: duplicate output UUID')
            seen.add(params['UUID'])
    require(not groups, 'Unclosed control flow group')

    if not product:
        return
    allowed = {'comment', 'getclipboard', 'gettext', 'text.match', 'conditional',
               'alert', 'exit', 'choosefrommenu', 'askllm', 'setclipboard', 'nothing'}
    require(all(a['WFWorkflowActionIdentifier'] in {ACTION_PREFIX + k for k in allowed}
                for a in actions), 'Product contains an unexpected action; review its data access')
    models = [i for i, a in enumerate(actions) if a['WFWorkflowActionIdentifier'] == ACTION_PREFIX + 'askllm']
    copies = [i for i, a in enumerate(actions) if a['WFWorkflowActionIdentifier'] == ACTION_PREFIX + 'setclipboard']
    require(len(models) == 1, 'Expected one model action')
    require(actions[models[0]]['WFWorkflowActionParameters']['WFLLMModel'] == 'Apple Intelligence on Device',
            'Product model must explicitly be on-device')
    require(len(copies) == 1 and copies[0] > models[0], 'Expected one clipboard write after the model')
    copy_index = copies[0]
    previous = actions[copy_index - 1]
    require(previous['WFWorkflowActionIdentifier'] == ACTION_PREFIX + 'alert'
            and previous['WFWorkflowActionParameters'].get('WFAlertActionCancelButtonShown') is True,
            'Clipboard write must immediately follow cancellable preview confirmation')
    copy = actions[copy_index]['WFWorkflowActionParameters']
    require(copy.get('WFLocalOnly') is True, 'Result must be copied locally')
    require(copy.get('WFInput', {}).get('Value', {}).get('OutputUUID') == identifier('helper-replacement'),
            'Clipboard write must use the actual replacement output')
    require(actions[-1]['WFWorkflowActionIdentifier'] == ACTION_PREFIX + 'nothing',
            'Product must clear its implicit return value')


def validate_repository(root: Path = ROOT) -> None:
    factories = {'EntryProbe': smoke_probe, 'ClipboardProbe': clipboard_probe,
                 'ModelProbe': model_probe, 'EnglishHelper': english_helper}
    manifest = json.loads((root / 'dist/manifest.json').read_text(encoding='utf-8'))
    require(len(manifest) == len(factories), 'Unexpected manifest entries')
    entries = {entry['source']: entry for entry in manifest}
    require(len(entries) == len(manifest), 'Duplicate manifest source entries')
    for slug, factory in factories.items():
        source_path = f'shortcuts/{slug}.plist'
        source = root / source_path
        raw = source.read_bytes()
        data = plistlib.loads(raw)
        require(data == factory(), f'{source_path} is stale; regenerate it')
        validate_workflow(data, product=(slug == 'EnglishHelper'))
        entry = entries[source_path]
        require(entry['name'] == data['WFWorkflowName'], f'{source_path}: manifest name mismatch')
        require(entry['actions'] == len(data['WFWorkflowActions']), f'{source_path}: action count mismatch')
        require(entry['source_sha256'] == hashlib.sha256(raw).hexdigest(), f'{source_path}: source hash mismatch')
        require(entry['file'] == f"dist/{data['WFWorkflowName']}.shortcut", 'Unexpected installable filename')
        signed = root / entry['file']
        if signed.exists():
            require(entry['file_sha256'] == hashlib.sha256(signed.read_bytes()).hexdigest(),
                    f'{signed.name}: package hash mismatch')
        else:
            require(entry['status'] == 'source-only' and entry['file_sha256'] is None,
                    f'{signed.name}: declared package is missing')
        print(f'Validated generated source, references, control flow and manifest: {slug}')


if __name__ == '__main__':
    validate_repository()
