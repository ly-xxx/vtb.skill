#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable


GENERIC_CATEGORY_RULES = {
    "story_openers": [
        r"今天",
        r"昨天",
        r"最近",
        r"刚刚",
        r"刚才",
        r"前两天",
        r"那天",
        r"之前",
        r"后来",
        r"有一次",
    ],
    "incident_broadcast": [
        r"直播",
        r"开播",
        r"下播",
        r"翻唱",
        r"游戏",
        r"录播",
        r"预告",
        r"发生",
        r"出事",
        r"现场",
        r"消息",
        r"整活",
    ],
    "self_reference": [
        r"我",
        r"本人",
        r"自己",
    ],
    "fan_address": [
        r"大家",
        r"你们",
        r"各位",
        r"朋友们",
        r"同志们",
    ],
    "reaction_pivots": [
        r"不是",
        r"怎么",
        r"什么",
        r"等一下",
        r"真的假的",
        r"好怪",
        r"啊",
        r"诶",
    ],
}


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def dedupe(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    values: list[str] = []
    for item in items:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        values.append(text)
    return values


def manifest_root(target_path: Path) -> Path:
    return target_path.parent.parent.parent


def _find_single_target(root: Path) -> Path | None:
    targets_dir = root / "sources" / "targets"
    if not targets_dir.exists():
        return None
    matches = sorted(targets_dir.glob("*.json"))
    if len(matches) == 1:
        return matches[0]
    return None


def discover_target_path(
    explicit: str | None = None,
    *,
    search_from: Path | None = None,
    script_file: str | Path | None = None,
) -> Path | None:
    if explicit:
        return Path(explicit).expanduser().resolve()

    candidates: list[Path] = []
    if search_from:
        candidates.append(search_from.expanduser().resolve())
    if script_file:
        script_path = Path(script_file).expanduser().resolve()
        candidates.append(script_path.parent)
        candidates.append(script_path.parent.parent)

    visited: set[Path] = set()
    for candidate in candidates:
        for root in [candidate, *candidate.parents]:
            if root in visited:
                continue
            visited.add(root)
            target = _find_single_target(root)
            if target:
                return target.resolve()
    return None


def load_target_manifest(
    explicit: str | None = None,
    *,
    search_from: Path | None = None,
    script_file: str | Path | None = None,
) -> tuple[dict | None, Path | None]:
    target_path = discover_target_path(explicit, search_from=search_from, script_file=script_file)
    if not target_path or not target_path.exists():
        return None, None

    payload = load_json(target_path)
    if not isinstance(payload, dict):
        return None, target_path
    return payload, target_path


def canonical_source(manifest: dict | None, key: str) -> dict:
    if not isinstance(manifest, dict):
        return {}
    sources = manifest.get("canonical_sources")
    if not isinstance(sources, dict):
        return {}
    source = sources.get(key)
    return source if isinstance(source, dict) else {}


def collection_defaults(manifest: dict | None) -> dict:
    if not isinstance(manifest, dict):
        return {}
    defaults = manifest.get("collection_defaults")
    return defaults if isinstance(defaults, dict) else {}


def style_hints(manifest: dict | None) -> dict:
    if not isinstance(manifest, dict):
        return {}
    hints = manifest.get("style_hints")
    return hints if isinstance(hints, dict) else {}


def manifest_aliases(manifest: dict | None) -> list[str]:
    hints = style_hints(manifest)
    values: list[str] = []
    display_name = (manifest or {}).get("display_name") if isinstance(manifest, dict) else None
    if isinstance(display_name, str):
        values.append(display_name)
    for key in ("aliases", "self_reference", "fandom_aliases"):
        field = hints.get(key)
        if isinstance(field, list):
            values.extend(str(item) for item in field)
    return dedupe(values)


def manifest_search_terms(manifest: dict | None) -> list[str]:
    defaults = collection_defaults(manifest)
    hints = style_hints(manifest)
    values: list[str] = []
    values.extend(manifest_aliases(manifest))
    keywords = defaults.get("bilibili_search_keywords")
    if isinstance(keywords, list):
        values.extend(str(item) for item in keywords)
    key_phrases = hints.get("key_phrases")
    if isinstance(key_phrases, list):
        values.extend(str(item) for item in key_phrases)
    return dedupe(values)


def manifest_stt_terms(manifest: dict | None) -> list[str]:
    if not isinstance(manifest, dict):
        return []

    voice = manifest.get("voice_pipeline")
    hints = style_hints(manifest)
    values: list[str] = []
    if isinstance(voice, dict):
        hotwords = voice.get("stt_hotwords")
        if isinstance(hotwords, list):
            values.extend(str(item) for item in hotwords)
    values.extend(manifest_aliases(manifest))
    key_phrases = hints.get("key_phrases")
    if isinstance(key_phrases, list):
        values.extend(str(item) for item in key_phrases)
    return dedupe(values)


def manifest_transcript_formats(manifest: dict | None) -> list[str]:
    defaults = collection_defaults(manifest)
    if isinstance(manifest, dict):
        voice = manifest.get("voice_pipeline")
        if isinstance(voice, dict):
            formats = voice.get("transcript_formats")
            if isinstance(formats, list):
                return dedupe(str(item).lower() for item in formats)

    formats = defaults.get("transcript_formats")
    if isinstance(formats, list):
        return dedupe(str(item).lower() for item in formats)
    return ["json", "srt", "vtt", "tsv", "txt"]


def build_category_rules(manifest: dict | None) -> dict[str, list[str]]:
    rules = {key: list(values) for key, values in GENERIC_CATEGORY_RULES.items()}
    hints = style_hints(manifest)

    direct_rules = hints.get("category_rules")
    if isinstance(direct_rules, dict):
        for category, values in direct_rules.items():
            if category not in rules or not isinstance(values, list):
                continue
            rules[category].extend(str(item) for item in values if str(item).strip())

    hint_mapping = {
        "story_openers": "story_openers",
        "incident_terms": "incident_broadcast",
        "self_reference": "self_reference",
        "fandom_aliases": "fan_address",
        "reaction_pivots": "reaction_pivots",
    }
    for hint_key, category in hint_mapping.items():
        values = hints.get(hint_key)
        if not isinstance(values, list):
            continue
        rules[category].extend(re.escape(str(item).strip()) for item in values if str(item).strip())

    return {key: dedupe(values) for key, values in rules.items()}
