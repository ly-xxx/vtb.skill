#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from target_manifest import load_target_manifest, manifest_root, manifest_transcript_formats


def load_video_details(path: Path) -> list[dict]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    return [item for item in payload if isinstance(item, dict)]


def compile_patterns(values: list[str]) -> list[re.Pattern[str]]:
    patterns = []
    for value in values:
        value = value.strip()
        if not value:
            continue
        patterns.append(re.compile(value, re.I))
    return patterns


def title_matches(title: str, include_patterns: list[re.Pattern[str]], exclude_patterns: list[re.Pattern[str]]) -> bool:
    if include_patterns and not any(pattern.search(title) for pattern in include_patterns):
        return False
    if exclude_patterns and any(pattern.search(title) for pattern in exclude_patterns):
        return False
    return True


def select_candidates(
    items: list[dict],
    *,
    explicit_bvids: list[str],
    include_patterns: list[re.Pattern[str]],
    exclude_patterns: list[re.Pattern[str]],
    min_duration: int,
    max_duration: int,
    limit: int,
) -> list[dict]:
    selected = []
    seen = set()

    by_bvid = {str(item.get("bvid")): item for item in items if item.get("bvid")}
    for bvid in explicit_bvids:
        item = by_bvid.get(bvid)
        if not item:
            continue
        selected.append(item)
        seen.add(bvid)

    for item in items:
        bvid = str(item.get("bvid") or "").strip()
        if not bvid or bvid in seen:
            continue
        title = str(item.get("title") or "")
        duration = int(item.get("duration") or 0)
        if duration < min_duration:
            continue
        if max_duration > 0 and duration > max_duration:
            continue
        if not title_matches(title, include_patterns, exclude_patterns):
            continue
        selected.append(item)
        seen.add(bvid)
        if limit > 0 and len(selected) >= limit:
            break

    if limit > 0:
        return selected[:limit]
    return selected


def run_step(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    combined = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
    return result.returncode, combined


def count_segments(transcript_dir: Path, audio_path: Path) -> int | None:
    json_path = transcript_dir / f"{audio_path.stem}.json"
    if not json_path.exists():
        return None
    try:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    segments = payload.get("segments")
    if not isinstance(segments, list):
        return None
    return len(segments)


def resolve_default_path(root: Path | None, relative: str) -> Path:
    if root:
        return root / relative
    return Path(relative)


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch download and transcribe selected Bilibili videos.")
    parser.add_argument("--target", help="Optional target manifest path")
    parser.add_argument("--video-details", help="Video details json path")
    parser.add_argument("--media-dir", help="Directory for downloaded media")
    parser.add_argument("--transcript-dir", help="Directory for transcript outputs")
    parser.add_argument("--hotwords-file", help="Hotwords file for transcription")
    parser.add_argument("--bvid", action="append", default=[], help="Explicit BVID to process; may be repeated")
    parser.add_argument("--include-title", action="append", default=[], help="Regex pattern; title must match one if provided")
    parser.add_argument("--exclude-title", action="append", default=[], help="Regex pattern; title must not match any")
    parser.add_argument("--min-duration", type=int, default=30, help="Minimum video duration in seconds")
    parser.add_argument("--max-duration", type=int, default=900, help="Maximum video duration in seconds; 0 disables cap")
    parser.add_argument("--limit", type=int, default=3, help="Maximum number of videos to process")
    parser.add_argument("--model", default="small", help="Whisper model passed to transcribe_audio.py")
    parser.add_argument("--language", default="zh", help="Language passed to transcribe_audio.py")
    parser.add_argument("--device", default="auto", help="Device passed to transcribe_audio.py")
    parser.add_argument("--compute-type", default="auto", help="Compute type passed to transcribe_audio.py")
    parser.add_argument("--beam-size", type=int, default=5, help="Beam size passed to transcribe_audio.py")
    parser.add_argument("--initial-prompt", help="Inline prompt passed to transcribe_audio.py")
    parser.add_argument("--initial-prompt-file", help="Prompt file passed to transcribe_audio.py")
    parser.add_argument("--no-vad", action="store_true", help="Disable VAD in transcription")
    parser.add_argument("--no-word-timestamps", action="store_true", help="Disable word timestamps in transcription")
    parser.add_argument("--retry-no-vad", action="store_true", help="Retry with --no-vad when first pass returns zero segments")
    parser.add_argument("--force", action="store_true", help="Overwrite existing media and transcript files")
    args = parser.parse_args()

    manifest, target_path = load_target_manifest(args.target, search_from=Path.cwd(), script_file=__file__)
    root = manifest_root(target_path) if target_path else None
    target_slug = str((manifest or {}).get("slug") or "").strip()

    video_details_path = Path(args.video_details).expanduser() if args.video_details else resolve_default_path(root, "sources/raw/bilibili/video_details.json")
    media_dir = Path(args.media_dir).expanduser() if args.media_dir else resolve_default_path(root, "sources/media/bilibili_batch")
    transcript_dir = Path(args.transcript_dir).expanduser() if args.transcript_dir else resolve_default_path(root, "sources/transcripts/bilibili_batch")

    default_hotwords = resolve_default_path(root, f"sources/processed/{target_slug}-hotwords.txt") if target_slug else None
    fallback_hotwords = resolve_default_path(root, "sources/processed/corpus/hot_phrases.txt")
    if args.hotwords_file:
        hotwords_file = Path(args.hotwords_file).expanduser()
    elif default_hotwords and default_hotwords.exists():
        hotwords_file = default_hotwords
    elif fallback_hotwords.exists():
        hotwords_file = fallback_hotwords
    else:
        hotwords_file = default_hotwords or fallback_hotwords

    if args.initial_prompt_file:
        initial_prompt_file = Path(args.initial_prompt_file).expanduser()
    else:
        candidate = resolve_default_path(root, "sources/processed/corpus/stt_initial_prompt.txt")
        initial_prompt_file = candidate if candidate.exists() else None

    items = load_video_details(video_details_path)
    include_patterns = compile_patterns(args.include_title)
    exclude_patterns = compile_patterns(args.exclude_title)
    candidates = select_candidates(
        items,
        explicit_bvids=args.bvid,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        min_duration=args.min_duration,
        max_duration=args.max_duration,
        limit=args.limit,
    )

    manifest_payload = {
        "generated_at": None,
        "target": str(target_path) if target_path else None,
        "video_details": str(video_details_path),
        "media_dir": str(media_dir),
        "transcript_dir": str(transcript_dir),
        "hotwords_file": str(hotwords_file),
        "candidates": [],
    }

    script_root = Path(__file__).resolve().parent
    downloader = script_root / "download_bilibili_media_public.py"
    transcriber = script_root / "transcribe_audio.py"
    transcript_formats = ",".join(manifest_transcript_formats(manifest))

    for item in candidates:
        bvid = str(item.get("bvid"))
        title = str(item.get("title") or bvid)
        record = {
            "bvid": bvid,
            "title": title,
            "duration": item.get("duration"),
            "download": {"ok": False, "output": ""},
            "transcribe": {"ok": False, "output": ""},
        }

        download_cmd = [
            "python3",
            str(downloader),
            "--audio-only",
            "--output-dir",
            str(media_dir),
        ]
        if args.force:
            download_cmd.append("--force")
        download_cmd.append(bvid)

        rc, output = run_step(download_cmd)
        record["download"] = {"ok": rc == 0, "output": output}
        if rc != 0:
            manifest_payload["candidates"].append(record)
            continue

        audio_candidates = sorted(media_dir.glob(f"*{bvid}*.m4a"))
        if not audio_candidates:
            record["transcribe"] = {"ok": False, "output": "download succeeded but no .m4a file found"}
            manifest_payload["candidates"].append(record)
            continue

        audio_path = audio_candidates[0]
        transcribe_cmd = [
            "python3",
            str(transcriber),
            str(audio_path),
            "--output-dir",
            str(transcript_dir),
            "--model",
            args.model,
            "--language",
            args.language,
            "--device",
            args.device,
            "--compute-type",
            args.compute_type,
            "--beam-size",
            str(args.beam_size),
            "--formats",
            transcript_formats,
        ]
        if hotwords_file and hotwords_file.exists():
            transcribe_cmd.extend(["--hotwords-file", str(hotwords_file)])
        if args.initial_prompt:
            transcribe_cmd.extend(["--initial-prompt", args.initial_prompt])
        if initial_prompt_file and initial_prompt_file.exists():
            transcribe_cmd.extend(["--initial-prompt-file", str(initial_prompt_file)])
        if args.no_vad:
            transcribe_cmd.append("--no-vad")
        if args.no_word_timestamps:
            transcribe_cmd.append("--no-word-timestamps")

        rc, output = run_step(transcribe_cmd)
        retry_output = ""
        segment_count = count_segments(transcript_dir, audio_path) if rc == 0 else None

        if rc == 0 and segment_count == 0 and not args.no_vad and args.retry_no_vad:
            retry_cmd = [*transcribe_cmd, "--no-vad"]
            rc_retry, retry_output = run_step(retry_cmd)
            if rc_retry == 0:
                rc = 0
                segment_count = count_segments(transcript_dir, audio_path)
            else:
                rc = rc_retry

        record["transcribe"] = {
            "ok": rc == 0,
            "output": output,
            "retry_output": retry_output,
            "audio_path": str(audio_path),
            "segment_count": segment_count,
        }
        manifest_payload["candidates"].append(record)

    manifest_payload["generated_at"] = datetime.now(timezone.utc).isoformat()
    media_dir.mkdir(parents=True, exist_ok=True)
    transcript_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = transcript_dir / "batch-manifest.json"
    manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] manifest -> {manifest_path}")
    print(f"[OK] processed -> {len(candidates)} videos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
