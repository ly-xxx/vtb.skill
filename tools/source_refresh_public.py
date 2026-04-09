#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from target_manifest import canonical_source, collection_defaults, load_target_manifest, manifest_root, manifest_search_terms


def run_step(command: list[str]) -> int:
    print("[RUN]", " ".join(command))
    result = subprocess.run(command, check=False)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh public VTuber sources using stable collectors.")
    parser.add_argument(
        "--target",
        help="Target manifest path",
    )
    parser.add_argument(
        "--steps",
        default="weibo,bilibili,corpus",
        help="Comma-separated steps: weibo,bilibili,corpus",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Ignore existing bilibili outputs and avoid fallback reuse",
    )
    parser.add_argument(
        "--http-retries",
        type=int,
        default=6,
        help="HTTP retry attempts passed to bilibili collector",
    )
    parser.add_argument(
        "--retry-backoff",
        type=float,
        default=1.8,
        help="Base retry backoff passed to bilibili collector",
    )
    parser.add_argument(
        "--save-every",
        type=int,
        default=20,
        help="Partial flush cadence passed to long-running bilibili steps",
    )
    args = parser.parse_args()

    manifest, target_path = load_target_manifest(args.target, search_from=Path.cwd(), script_file=__file__)
    if not manifest or not target_path:
        raise SystemExit("target manifest not found; pass --target or run inside a skill directory that contains sources/targets/*.json")

    root = manifest_root(target_path)
    script_root = Path(__file__).resolve().parent
    defaults = collection_defaults(manifest)
    weibo = canonical_source(manifest, "weibo")
    bili = canonical_source(manifest, "bilibili")
    has_weibo = bool(str(weibo.get("uid") or "").strip())
    has_bili = bool(str(bili.get("mid") or "").strip())
    if not has_weibo and not has_bili:
        raise SystemExit(
            "no usable canonical source configured: need at least one of weibo(uid+domain) or bilibili(mid). "
            "If one source cannot be verified, leave it empty and continue with the other; if both are missing, stop and add a verified source first."
        )
    steps = {item.strip() for item in args.steps.split(",") if item.strip()}
    failures = 0

    if "weibo" in steps:
        uid = str(weibo.get("uid") or "").strip()
        domain = str(weibo.get("domain") or "").strip()
        if uid:
            command = [
                "python3",
                str(script_root / "collect_weibo_public.py"),
                "--uid",
                uid,
                "--force-html-spider",
                "--limit",
                str(defaults.get("weibo_limit", 300)),
                "--comments-per-post",
                str(defaults.get("weibo_comments_per_post", 10)),
                "--max-pages",
                str(defaults.get("weibo_max_pages", 40)),
                "--output-dir",
                str(root / "sources" / "raw" / "weibo"),
            ]
            if domain:
                command.extend(["--domain", domain])
            rc = run_step(command)
            failures += int(rc != 0)
        else:
            print("[WARN] weibo source is missing or unverifiable; continue with remaining sources")

    if "bilibili" in steps:
        mid = str(bili.get("mid") or "").strip()
        room_id = str(bili.get("room_id") or bili.get("short_id") or "").strip()
        keywords = ",".join(defaults.get("bilibili_search_keywords") or manifest_search_terms(manifest))
        if mid:
            command = [
                "python3",
                str(script_root / "collect_bilibili_public.py"),
                "--target",
                str(target_path),
                "--mid",
                mid,
                "--room-id",
                room_id,
                "--video-limit",
                str(defaults.get("bilibili_video_limit", 80)),
                "--dynamic-limit",
                str(defaults.get("bilibili_dynamic_limit", 20)),
                "--comment-limit",
                str(defaults.get("bilibili_comment_limit", 0)),
                "--comment-video-limit",
                str(defaults.get("bilibili_comment_video_limit", 10)),
                "--keywords",
                keywords,
                "--search-pages",
                str(defaults.get("bilibili_search_pages", 8)),
                "--playurl-limit",
                str(defaults.get("bilibili_playurl_limit", 0)),
                "--http-retries",
                str(args.http_retries),
                "--retry-backoff",
                str(args.retry_backoff),
                "--save-every",
                str(args.save_every),
                "--output-dir",
                str(root / "sources" / "raw" / "bilibili"),
            ]
            command.append("--fresh" if args.fresh else "--resume")
            rc = run_step(command)
            failures += int(rc != 0)
        else:
            print("[WARN] bilibili source is missing or unverifiable; continue with remaining sources")

    if "corpus" in steps:
        rc = run_step([
            "python3",
            str(script_root / "build_corpus_public.py"),
            "--target",
            str(target_path),
            "--raw-dir",
            str(root / "sources" / "raw"),
            "--transcript-dir",
            str(root / "sources" / "transcripts"),
            "--output-dir",
            str(root / "sources" / "processed" / "corpus"),
        ])
        failures += int(rc != 0)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
