"""Post history management using TSV files.

Tracks all generated posts through their lifecycle:
draft -> scheduled -> published (or failed).
"""

import csv
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

TSV_PATH = Path(__file__).resolve().parent.parent / "data" / "posts.tsv"

COLUMNS = [
    "id",
    "topic",
    "generated_content",
    "image_url",
    "format",
    "scheduled_date",
    "status",
    "review_required",
    "linkedin_post_id",
    "created_at",
    "published_at",
    "error",
]


def _ensure_file():
    """Create the TSV file with headers if it doesn't exist."""
    if not TSV_PATH.exists():
        TSV_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TSV_PATH, "w", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(COLUMNS)


def _read_all() -> list[dict]:
    """Read all rows from the TSV file."""
    _ensure_file()
    with open(TSV_PATH, "r", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return list(reader)


def _write_all(rows: list[dict]):
    """Overwrite the TSV file with the given rows."""
    _ensure_file()
    with open(TSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def add_post(
    topic: str,
    generated_content: str,
    scheduled_date: str,
    format: str = "text",
    review_required: bool = True,
    image_url: str = "",
) -> str:
    """Add a new post to the history. Returns the generated post ID."""
    _ensure_file()
    post_id = uuid.uuid4().hex[:8]
    row = {
        "id": post_id,
        "topic": topic,
        "generated_content": generated_content,
        "image_url": image_url,
        "format": format,
        "scheduled_date": scheduled_date,
        "status": "draft" if review_required else "scheduled",
        "review_required": "1" if review_required else "0",
        "linkedin_post_id": "",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "published_at": "",
        "error": "",
    }
    with open(TSV_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, delimiter="\t")
        writer.writerow(row)
    return post_id


def get_post(post_id: str) -> dict | None:
    """Get a single post by ID."""
    for row in _read_all():
        if row["id"] == post_id:
            return row
    return None


def get_posts_by_status(status: str) -> list[dict]:
    """Get all posts with a given status."""
    return [r for r in _read_all() if r["status"] == status]


def get_posts_by_date(date: str) -> list[dict]:
    """Get all posts scheduled for a given date (YYYY-MM-DD)."""
    return [r for r in _read_all() if r["scheduled_date"] == date]


def get_next_scheduled() -> dict | None:
    """Get the next post due for publishing (scheduled_date <= today)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    candidates = [
        r for r in _read_all()
        if r["status"] == "scheduled" and r["scheduled_date"] <= today
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda r: r["scheduled_date"])
    return candidates[0]


def update_post(post_id: str, **fields) -> bool:
    """Update specific fields on a post. Returns True if found."""
    rows = _read_all()
    found = False
    for row in rows:
        if row["id"] == post_id:
            for key, value in fields.items():
                if key in COLUMNS:
                    row[key] = value
            found = True
            break
    if found:
        _write_all(rows)
    return found


def delete_post(post_id: str) -> bool:
    """Delete a post by ID. Returns True if found and removed."""
    rows = _read_all()
    filtered = [r for r in rows if r["id"] != post_id]
    if len(filtered) < len(rows):
        _write_all(filtered)
        return True
    return False


def get_all_posts() -> list[dict]:
    """Get all posts, sorted by scheduled_date descending."""
    rows = _read_all()
    rows.sort(key=lambda r: r.get("scheduled_date", ""), reverse=True)
    return rows


def get_recent_topics(limit: int = 50) -> list[str]:
    """Get recent post topics for deduplication."""
    rows = _read_all()
    rows.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return [r["topic"] for r in rows[:limit]]
