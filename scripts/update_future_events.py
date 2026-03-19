from __future__ import annotations

import argparse
from datetime import date
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.future_event_updater import (
    DEFAULT_MAX_SOURCE_CHARS,
    DEFAULT_NIM_BASE_URL,
    DEFAULT_NIM_MODEL,
    build_dry_run_update,
    clip_source_text,
    fetch_url_text,
    load_api_key,
    load_sources,
    request_nim_summary,
    write_snapshot,
    write_snapshot_json,
    write_update,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch official future event pages and update the repo with Nemotron-generated summaries."
    )
    parser.add_argument(
        "--sources-file",
        default=str(ROOT / "automation" / "future_event_sources.json"),
    )
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_SOURCE_CHARS)
    parser.add_argument(
        "--base-url",
        default=os.environ.get("NIM_BASE_URL", DEFAULT_NIM_BASE_URL),
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("NIM_MODEL", DEFAULT_NIM_MODEL),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run_date = date.fromisoformat(args.date)
    sources = load_sources(Path(args.sources_file))
    if args.only:
        allowed = set(args.only)
        sources = [source for source in sources if source.id in allowed]

    updates = []
    for source in sources:
        source_text = fetch_url_text(source.url, timeout=args.timeout)
        clipped = clip_source_text(source_text, max_chars=args.max_chars)
        if args.dry_run:
            update = build_dry_run_update(source, run_date, clipped)
        else:
            api_key = load_api_key()
            update = request_nim_summary(
                source=source,
                source_text=clipped,
                run_date=run_date,
                api_key=api_key,
                base_url=args.base_url,
                model=args.model,
            )
        write_update(ROOT, update, run_date)
        updates.append(update)

    write_snapshot(ROOT, updates, run_date)
    write_snapshot_json(ROOT, updates, run_date, model=args.model)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
