from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable, List


DEFAULT_NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_NIM_MODEL = "nvidia/nemotron-3-super-120b-a12b"
DEFAULT_MAX_SOURCE_CHARS = 20000


@dataclass(frozen=True)
class EventSource:
    id: str
    title: str
    url: str
    category: str


@dataclass(frozen=True)
class EventUpdate:
    source: EventSource
    status: str
    event_name: str
    event_date: str | None
    location: str | None
    summary: str
    why_it_matters: str
    key_signals: List[str]
    confidence_note: str
    source_url: str


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        cleaned = normalize_whitespace(data)
        if cleaned:
            self._chunks.append(cleaned)

    def text(self) -> str:
        return normalize_whitespace(" ".join(self._chunks))


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_text_from_html(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    return parser.text()


def load_sources(path: Path) -> list[EventSource]:
    raw_sources = json.loads(path.read_text())
    return [EventSource(**item) for item in raw_sources]


def fetch_url_text(url: str, timeout: int = 20) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "nvidia-systems-learning-lab-updater/0.1",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8", errors="replace")
    return extract_text_from_html(body)


def clip_source_text(text: str, max_chars: int = DEFAULT_MAX_SOURCE_CHARS) -> str:
    normalized = normalize_whitespace(text)
    return normalized[:max_chars]


def build_messages(source: EventSource, source_text: str, run_date: date) -> list[dict[str, Any]]:
    system = (
        "You update a public research repository about NVIDIA systems architecture. "
        "Only extract confirmed future event information from the provided official source page. "
        "If the page does not clearly confirm a future event date, mark the item as watchlist. "
        "Return strict JSON with keys: "
        "status, event_name, event_date, location, summary, why_it_matters, key_signals, confidence_note. "
        "status must be one of confirmed, watchlist, or skip. "
        "event_date must be a single ISO date or an ISO date range like YYYY-MM-DD/YYYY-MM-DD, or null. "
        "key_signals must be an array of 1 to 5 short strings. "
        "Do not invent facts. Do not include markdown."
    )
    user = {
        "source_id": source.id,
        "source_title": source.title,
        "source_category": source.category,
        "source_url": source.url,
        "run_date": run_date.isoformat(),
        "page_text": source_text,
    }
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(user)},
    ]


def _extract_json_blob(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("model response did not contain a JSON object")
    return text[start : end + 1]


def request_nim_summary(
    source: EventSource,
    source_text: str,
    run_date: date,
    api_key: str,
    base_url: str = DEFAULT_NIM_BASE_URL,
    model: str = DEFAULT_NIM_MODEL,
    timeout: int = 60,
) -> EventUpdate:
    payload = {
        "model": model,
        "messages": build_messages(source, source_text, run_date),
        "temperature": 0.1,
        "max_tokens": 700,
    }
    endpoint = urllib.parse.urljoin(base_url.rstrip("/") + "/", "chat/completions")
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw_response = json.loads(response.read().decode("utf-8"))
    content = raw_response["choices"][0]["message"]["content"]
    parsed = json.loads(_extract_json_blob(content))
    return EventUpdate(
        source=source,
        status=str(parsed["status"]),
        event_name=str(parsed["event_name"]),
        event_date=parsed.get("event_date"),
        location=parsed.get("location"),
        summary=str(parsed["summary"]),
        why_it_matters=str(parsed["why_it_matters"]),
        key_signals=[str(item) for item in parsed.get("key_signals", [])][:5],
        confidence_note=str(parsed.get("confidence_note", "")),
        source_url=source.url,
    )


def sort_key(update: EventUpdate) -> tuple[int, str, str]:
    if update.status != "confirmed" or not update.event_date:
        return (1, "9999-99-99", update.event_name.lower())
    start = update.event_date.split("/")[0]
    return (0, start, update.event_name.lower())


def render_update_markdown(update: EventUpdate, run_date: date) -> str:
    signals = "\n".join(f"- {signal}" for signal in update.key_signals) or "- None"
    event_date = update.event_date or "Unconfirmed"
    location = update.location or "Unconfirmed"
    return f"""# {update.event_name}

- Run date: {run_date.isoformat()}
- Status: {update.status}
- Event date: {event_date}
- Location: {location}
- Source: {update.source_url}

## Summary

{update.summary}

## Why It Matters

{update.why_it_matters}

## Key Signals

{signals}

## Confidence Note

{update.confidence_note}
"""


def write_update(root: Path, update: EventUpdate, run_date: date) -> Path:
    event_dir = root / "events" / update.source.id / "updates"
    event_dir.mkdir(parents=True, exist_ok=True)
    out_path = event_dir / f"{run_date.isoformat()}.md"
    out_path.write_text(render_update_markdown(update, run_date))
    return out_path


def render_snapshot(updates: Iterable[EventUpdate], run_date: date) -> str:
    ordered = sorted(updates, key=sort_key)
    confirmed_lines: list[str] = []
    watchlist_lines: list[str] = []
    for update in ordered:
        line = (
            f"- **{update.event_name}**"
            f" | status: `{update.status}`"
            f" | date: `{update.event_date or 'unconfirmed'}`"
            f" | location: `{update.location or 'unconfirmed'}`"
            f" | source: {update.source_url}"
        )
        detail = f"  {update.summary}"
        if update.status == "confirmed":
            confirmed_lines.extend([line, detail])
        else:
            watchlist_lines.extend([line, detail])
    confirmed_block = "\n".join(confirmed_lines) or "- None"
    watchlist_block = "\n".join(watchlist_lines) or "- None"
    return f"""# Generated Future Events Snapshot

Generated on **{run_date.isoformat()}** by the Nemotron-backed updater.

This page is generated from official event pages in `automation/future_event_sources.json`.

## Confirmed Future Events

{confirmed_block}

## Watchlist

{watchlist_block}
"""


def write_snapshot(root: Path, updates: Iterable[EventUpdate], run_date: date) -> Path:
    snapshot_path = root / "docs" / "future-events-generated.md"
    snapshot_path.write_text(render_snapshot(updates, run_date))
    return snapshot_path


def write_snapshot_json(
    root: Path,
    updates: Iterable[EventUpdate],
    run_date: date,
    model: str = DEFAULT_NIM_MODEL,
) -> Path:
    payload = {
        "generated_on": run_date.isoformat(),
        "model": model,
        "items": [
            {
                "source_id": update.source.id,
                "source_title": update.source.title,
                "status": update.status,
                "event_name": update.event_name,
                "event_date": update.event_date,
                "location": update.location,
                "summary": update.summary,
                "why_it_matters": update.why_it_matters,
                "key_signals": update.key_signals,
                "confidence_note": update.confidence_note,
                "source_url": update.source_url,
            }
            for update in sorted(updates, key=sort_key)
        ],
    }
    out_path = root / "data" / "future_event_snapshot.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n")
    return out_path


def build_dry_run_update(source: EventSource, run_date: date, source_text: str) -> EventUpdate:
    excerpt = clip_source_text(source_text, 220)
    return EventUpdate(
        source=source,
        status="watchlist",
        event_name=source.title,
        event_date=None,
        location=None,
        summary=f"Dry run only. Source fetched and clipped successfully. Excerpt: {excerpt}",
        why_it_matters="Dry run mode verifies fetch and file generation without calling NIM.",
        key_signals=["dry-run", source.category],
        confidence_note=f"No model call was made on {run_date.isoformat()}.",
        source_url=source.url,
    )


def load_api_key() -> str:
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        raise RuntimeError("NVIDIA_API_KEY is required for live NIM updates")
    return api_key
