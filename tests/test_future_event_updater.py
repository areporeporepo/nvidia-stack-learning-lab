from datetime import date

from automation.future_event_updater import (
    EventSource,
    EventUpdate,
    extract_text_from_html,
    render_snapshot,
    render_update_markdown,
    sort_key,
)


def test_extract_text_from_html_skips_script_and_style() -> None:
    html = """
    <html>
      <head><style>.x { color: red; }</style><script>ignore_me()</script></head>
      <body><h1>COMPUTEX 2026</h1><p>June 2-5, 2026</p></body>
    </html>
    """
    text = extract_text_from_html(html)
    assert "COMPUTEX 2026" in text
    assert "June 2-5, 2026" in text
    assert "ignore_me" not in text
    assert "color: red" not in text


def test_render_update_markdown_includes_core_fields() -> None:
    source = EventSource(
        id="computex-2026",
        title="COMPUTEX 2026",
        url="https://example.com",
        category="conference",
    )
    update = EventUpdate(
        source=source,
        status="confirmed",
        event_name="COMPUTEX 2026",
        event_date="2026-06-02/2026-06-05",
        location="Taipei, Taiwan",
        summary="Major OEM and platform event.",
        why_it_matters="Strong signal for rack and platform announcements.",
        key_signals=["Rubin", "liquid cooling"],
        confidence_note="Official event page includes date.",
        source_url=source.url,
    )
    markdown = render_update_markdown(update, date(2026, 3, 19))
    assert "COMPUTEX 2026" in markdown
    assert "2026-06-02/2026-06-05" in markdown
    assert "Taipei, Taiwan" in markdown
    assert "- Rubin" in markdown


def test_snapshot_sorts_confirmed_before_watchlist() -> None:
    source = EventSource(
        id="siggraph-2026",
        title="SIGGRAPH 2026",
        url="https://example.com",
        category="conference",
    )
    confirmed = EventUpdate(
        source=source,
        status="confirmed",
        event_name="SIGGRAPH 2026",
        event_date="2026-07-19/2026-07-23",
        location="Los Angeles, California",
        summary="Confirmed conference dates.",
        why_it_matters="Future Jensen speaking slot.",
        key_signals=["Jensen Huang"],
        confidence_note="Official conference page.",
        source_url=source.url,
    )
    watchlist = EventUpdate(
        source=source,
        status="watchlist",
        event_name="Stanford Jensen Watch",
        event_date=None,
        location=None,
        summary="No dated page yet.",
        why_it_matters="Potential future speaking event.",
        key_signals=["watchlist"],
        confidence_note="No dated source page.",
        source_url=source.url,
    )
    rendered = render_snapshot([watchlist, confirmed], date(2026, 3, 19))
    assert rendered.index("SIGGRAPH 2026") < rendered.index("Stanford Jensen Watch")
    assert sort_key(confirmed) < sort_key(watchlist)
