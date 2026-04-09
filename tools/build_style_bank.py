#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from target_manifest import build_category_rules, load_target_manifest


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                continue
            if isinstance(payload, dict):
                rows.append(payload)
    return rows


def char_mix(text: str) -> tuple[int, int]:
    cjk = 0
    total = 0
    for char in text:
        if char.isspace():
            continue
        total += 1
        if "\u4e00" <= char <= "\u9fff":
            cjk += 1
    return cjk, total


def classify_text(text: str, category_rules: dict[str, list[str]]) -> list[str]:
    matched = []
    for category, patterns in category_rules.items():
        if any(re.search(pattern, text, flags=re.I) for pattern in patterns):
            matched.append(category)
    return matched


def score_text(row: dict, text: str) -> tuple[float, int]:
    cjk, total = char_mix(text)
    cjk_ratio = (cjk / total) if total else 0.0
    quality = float(row.get("quality_score") or 0.0)
    length_bonus = min(total, 45) / 45.0
    score = quality * 0.7 + cjk_ratio * 20.0 + length_bonus * 10.0
    return score, total


def collect_examples(
    rows: list[dict],
    *,
    max_per_category: int,
    category_rules: dict[str, list[str]],
) -> dict[str, list[dict]]:
    buckets: dict[str, list[dict]] = defaultdict(list)
    seen_texts: set[str] = set()

    sorted_rows = sorted(
        rows,
        key=lambda row: (float(row.get("quality_score") or 0.0), row.get("char_count") or 0),
        reverse=True,
    )

    for row in sorted_rows:
        text = normalize_text(str(row.get("text") or ""))
        if not text:
            continue
        if text in seen_texts:
            continue

        cjk, total = char_mix(text)
        if total < 8:
            continue
        if total > 80:
            continue
        if total and (cjk / total) < 0.35:
            continue

        categories = classify_text(text, category_rules)
        if not categories:
            continue

        score, char_count = score_text(row, text)
        example = {
            "text": text,
            "bvid": row.get("bvid"),
            "title": row.get("title"),
            "quality_score": row.get("quality_score"),
            "char_count": char_count,
            "score": round(score, 2),
            "source_json": row.get("source_json"),
            "start": row.get("start"),
            "end": row.get("end"),
        }

        accepted = False
        for category in categories:
            if len(buckets[category]) >= max_per_category:
                continue
            buckets[category].append(example)
            accepted = True
        if accepted:
            seen_texts.add(text)

    for category, examples in buckets.items():
        examples.sort(key=lambda item: (item["score"], item["char_count"]), reverse=True)

    return dict(buckets)


def render_markdown(
    examples: dict[str, list[dict]],
    *,
    target_name: str | None,
    input_name: str,
) -> str:
    lines = [
        "# Style Bank",
        "",
        f"这份风格片段库从 `{input_name}` 自动抽取，用于沉淀 `{target_name or '目标角色'}` 的稳定表达片段。",
        "",
        "使用方式：",
        "",
        "- 不要整段照抄。",
        "- 重点学习句式推进、口播节奏、自称方式和互动结构。",
        "- 当多个类别同时命中时，优先模仿节奏，不要机械复制字面内容。",
        "",
    ]

    labels = {
        "story_openers": "Story Openers",
        "incident_broadcast": "Incident Broadcast",
        "self_reference": "Self Reference",
        "fan_address": "Fan Address",
        "reaction_pivots": "Reaction Pivots",
    }

    for category in ["story_openers", "incident_broadcast", "self_reference", "fan_address", "reaction_pivots"]:
        rows = examples.get(category) or []
        lines.append(f"## {labels[category]}")
        lines.append("")
        if not rows:
            lines.append("- 暂无样本")
            lines.append("")
            continue
        for row in rows[:10]:
            lines.append(f"- `{row['text']}`")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def resolve_input_path(input_path: Path) -> tuple[Path, list[dict], list[str]]:
    tried: list[str] = []
    candidates: list[Path] = []
    seen: set[Path] = set()

    def add_candidate(path: Path) -> None:
        resolved = path.expanduser()
        if resolved in seen:
            return
        seen.add(resolved)
        candidates.append(resolved)

    add_candidate(input_path)

    parent = input_path.parent
    if input_path.name == "transcript_train_recommended.jsonl":
        add_candidate(parent / "transcript_train_high.jsonl")
        add_candidate(parent / "transcript_train_ready.jsonl")
    elif input_path.name == "transcript_train_high.jsonl":
        add_candidate(parent / "transcript_train_ready.jsonl")

    for candidate in candidates:
        tried.append(str(candidate))
        rows = load_jsonl(candidate)
        if rows:
            return candidate, rows, tried

    return input_path, [], tried


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a style bank from recommended transcript training data.")
    parser.add_argument("--target", help="Optional target manifest path")
    parser.add_argument("--input-jsonl", default="sources/processed/training/transcript_train_recommended.jsonl", help="Recommended transcript JSONL")
    parser.add_argument("--output-json", default="sources/processed/style-bank.json", help="Style bank JSON output")
    parser.add_argument("--output-md", default="references/style-bank.md", help="Style bank Markdown output")
    parser.add_argument("--max-per-category", type=int, default=24, help="Maximum examples per category")
    args = parser.parse_args()

    input_path = Path(args.input_jsonl).expanduser()
    output_json = Path(args.output_json).expanduser()
    output_md = Path(args.output_md).expanduser()
    manifest, target_path = load_target_manifest(args.target, search_from=Path.cwd(), script_file=__file__)
    category_rules = build_category_rules(manifest)
    target_name = str((manifest or {}).get("display_name") or "").strip() or None

    resolved_input_path, rows, tried_inputs = resolve_input_path(input_path)
    examples = collect_examples(rows, max_per_category=args.max_per_category, category_rules=category_rules)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": str(target_path) if target_path else None,
        "input_jsonl": str(resolved_input_path),
        "requested_input_jsonl": str(input_path),
        "tried_inputs": tried_inputs,
        "category_counts": {key: len(value) for key, value in examples.items()},
        "examples": examples,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    output_md.write_text(
        render_markdown(examples, target_name=target_name, input_name=resolved_input_path.name),
        encoding="utf-8",
    )

    if resolved_input_path != input_path:
        print(f"[INFO] requested input was empty, fallback -> {resolved_input_path}")
    print(f"[OK] style bank json -> {output_json}")
    print(f"[OK] style bank md   -> {output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
