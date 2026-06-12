"""/sl — custom session list slash command.

Reads column config from ~/.hermes/session_list_config.yaml and renders
sessions with user-specified columns and widths.

Special column: field "#" renders as the row index (1-based), compatible
with /resume <number>.

Survives `hermes update` because it lives in ~/.hermes/plugins/.
"""
from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Optional


# ── Helpers ──────────────────────────────────────────────────────────

def _hermes_home() -> Path:
    import os
    return Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))


def _as_float(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(v)
    except (ValueError, TypeError):
        return v


def _relative_time(ts) -> str:
    ts = _as_float(ts)
    if not ts:
        return "?"
    delta = time.time() - ts
    if delta < 60:
        return "just now"
    if delta < 3600:
        return f"{int(delta / 60)}m ago"
    if delta < 86400:
        return f"{int(delta / 3600)}h ago"
    if delta < 172800:
        return "yesterday"
    if delta < 604800:
        return f"{int(delta / 86400)}d ago"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")


def _fmt_tokens(session: dict, field: str) -> str:
    """Format token counts in human-readable form (e.g. '46.8K').
    
    Special computed fields:
      total_tokens = input + output
      net_input    = input - cache_read  (actual new prompt tokens)
      net_total    = net_input + output  (actual billable tokens)
    """
    inp = _as_float(session.get("input_tokens")) or 0
    out = _as_float(session.get("output_tokens")) or 0
    cache = _as_float(session.get("cache_read_tokens")) or 0

    if field == "total_tokens":
        raw = inp + out
    elif field == "net_input":
        raw = max(0, inp - cache)
    elif field == "net_total":
        raw = max(0, inp - cache) + out
    else:
        raw = _as_float(session.get(field)) or 0

    if raw >= 1_000_000:
        return f"{raw / 1_000_000:.1f}M"
    if raw >= 1_000:
        return f"{raw / 1_000:.1f}K"
    return str(int(raw))


def _format_value(session: dict, field: str, index: int = 0) -> str:
    """Format a single field value. *index* is the 1-based row number for '#' field."""
    if field == "#":
        return str(index)
    raw = session.get(field)
    if field == "last_active":
        return _relative_time(raw)
    if field in ("started_at", "ended_at"):
        ts = _as_float(raw)
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") if ts else "—"
    if field == "title":
        v = session.get(field)
        if v is None or v == "None" or str(v).strip() == "":
            return "—"
        return str(v)[:40]
    if field == "preview":
        return (str(raw) if raw else "")[:80]
    if field == "message_count":
        return str(int(_as_float(raw) or 0))
    if field == "model":
        return (str(raw) if raw else "?")[:30]
    if field == "source":
        return str(raw) if raw else "?"
    if field in ("input_tokens", "output_tokens", "cache_read_tokens",
                 "cache_write_tokens", "reasoning_tokens",
                 "total_tokens", "net_input", "net_total"):
        return _fmt_tokens(session, field)
    return str(raw) if raw is not None else ""


def _build_header(columns: list) -> str:
    parts = []
    for col in columns:
        w = col.get("width", 20)
        label = col["label"]
        parts.append(f"{label:<{w}}" if w else label)
    return "  ".join(parts)


def _build_row(columns: list, session: dict, index: int = 0) -> str:
    parts = []
    for col in columns:
        w = col.get("width", 20)
        val = _format_value(session, col["field"], index=index)
        if w == 0:
            parts.append(val)
        else:
            parts.append(f"{val[:w]:<{w}}")
    return "  ".join(parts)


# ── Slash command handler ────────────────────────────────────────────

def _handle_sl(raw_args: str) -> Optional[str]:
    """Handle /sl [limit] — show recent sessions with custom columns."""
    import yaml

    config_path = _hermes_home() / "session_list_config.yaml"

    # Load column config
    try:
        if config_path.exists():
            cfg = yaml.safe_load(config_path.read_text())
            columns = cfg.get("columns", [])
        else:
            columns = []
    except Exception:
        columns = []

    if not columns:
        columns = [
            {"field": "#", "width": 3, "label": "#"},
            {"field": "title", "width": 32, "label": "Title"},
            {"field": "preview", "width": 40, "label": "Preview"},
            {"field": "last_active", "width": 13, "label": "Last Active"},
            {"field": "id", "width": 0, "label": "ID"},
        ]

    # Parse limit from args
    limit = 20
    args = raw_args.strip().split()
    if args:
        try:
            limit = int(args[0])
        except ValueError:
            pass

    # Query sessions
    from hermes_state import SessionDB
    db = SessionDB()
    sessions = db.list_sessions_rich(exclude_sources=["tool"], limit=limit)

    if not sessions:
        return "(._.) No previous sessions yet."

    # Render
    header = _build_header(columns)
    sep = "─" * len(header)
    lines = [header, sep]
    for idx, s in enumerate(sessions, start=1):
        lines.append(_build_row(columns, s, index=idx))

    # Add hint for /resume
    lines.append("")
    lines.append("Use /resume <#> to continue a session. Example: /resume 2")

    return "\n".join(lines)


# ── Plugin registration ──────────────────────────────────────────────

def register(ctx) -> None:
    ctx.register_command(
        "sl",
        handler=_handle_sl,
        description="List recent sessions with custom columns (config: ~/.hermes/session_list_config.yaml)",
        args_hint="[limit]",
    )
