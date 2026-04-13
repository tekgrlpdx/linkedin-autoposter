#!/usr/bin/env python3
"""Scrape the user's own LinkedIn posts for persona building.

Supports two modes:
  1. API mode: fetches posts via LinkedIn API (requires r_member_social scope).
  2. Browser mode: accepts pre-scraped post text via stdin or file, for use
     when the API lacks read permissions (common with "Share on LinkedIn" product).

Usage:
    # API mode (if r_member_social scope is available)
    python .claude/skills/linkedin/scripts/scrape_posts.py [--count 20]

    # Browser mode (paste or pipe scraped text, posts separated by ---)
    python .claude/skills/linkedin/scripts/scrape_posts.py --from-file scraped.txt
    echo "post text" | python .claude/skills/linkedin/scripts/scrape_posts.py --from-stdin

Browser Scraping Guide (for Claude Code with Chrome MCP):
    1. Navigate to https://www.linkedin.com/in/me/recent-activity/all/
    2. Scroll to load desired number of posts
    3. Click all "see more" buttons to expand truncated posts
    4. Extract text with JS: document.querySelectorAll('.feed-shared-inline-show-more-text')
    5. Pipe the extracted text into this script with --from-stdin or --from-file
"""

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def extract_post_text(post: dict) -> str:
    """Extract the text content from a LinkedIn API post object."""
    # Posts API format (current)
    if "commentary" in post:
        return post.get("commentary", "")
    # UGC format (legacy)
    specific = post.get("specificContent", {})
    share = specific.get("com.linkedin.ugc.ShareContent", {})
    commentary = share.get("shareCommentary", {})
    return commentary.get("text", "")


def save_posts(texts: list[str], output_path: Path) -> None:
    """Write post texts to the output file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for i, text in enumerate(texts):
            if i > 0:
                f.write("\n\n---\n\n")
            f.write(text)
    print(f"Saved {len(texts)} posts to {output_path}")
    print("These will be used as writing style reference when generating new posts.")


def parse_browser_text(raw: str) -> list[str]:
    """Parse browser-scraped text into individual posts.

    Accepts text separated by '---' dividers (the format used when
    Claude extracts posts via Chrome MCP javascript_tool).
    Strips common LinkedIn artifacts like 'hashtag\\n' prefixes.
    """
    posts = []
    for chunk in raw.split("\n---\n"):
        text = chunk.strip()
        # Remove LinkedIn's "hashtag\n" prefix artifacts from browser scraping
        text = text.replace("hashtag\n", "")
        if len(text) > 20:
            posts.append(text)
    return posts


def scrape_via_api(count: int) -> list[str]:
    """Fetch posts via LinkedIn API. Requires r_member_social scope."""
    from src.linkedin import get_user_posts

    print(f"Fetching your {count} most recent LinkedIn posts via API...")
    posts = get_user_posts(count=count)

    if not posts:
        return []

    texts = []
    for post in posts:
        text = extract_post_text(post)
        if text.strip():
            texts.append(text.strip())
    return texts


def main():
    parser = argparse.ArgumentParser(
        description="Scrape your LinkedIn posts for persona building"
    )
    parser.add_argument("--count", type=int, default=20, help="Number of posts to fetch (API mode)")
    parser.add_argument(
        "--from-file",
        type=str,
        help="Read browser-scraped posts from a text file (posts separated by ---)",
    )
    parser.add_argument(
        "--from-stdin",
        action="store_true",
        help="Read browser-scraped posts from stdin (posts separated by ---)",
    )
    args = parser.parse_args()

    output_path = project_root / "samples" / "linkedin_posts.txt"

    # Browser mode: from file
    if args.from_file:
        filepath = Path(args.from_file)
        if not filepath.exists():
            print(f"ERROR: File not found: {filepath}")
            sys.exit(1)
        raw = filepath.read_text()
        texts = parse_browser_text(raw)
        if not texts:
            print("No post content found in file.")
            sys.exit(0)
        save_posts(texts, output_path)
        return

    # Browser mode: from stdin
    if args.from_stdin:
        raw = sys.stdin.read()
        texts = parse_browser_text(raw)
        if not texts:
            print("No post content found in stdin.")
            sys.exit(0)
        save_posts(texts, output_path)
        return

    # API mode (default)
    try:
        texts = scrape_via_api(args.count)
    except Exception as e:
        print(f"ERROR: Failed to fetch posts via API: {e}")
        print()
        print("This usually means your LinkedIn app doesn't have the r_member_social scope.")
        print("The 'Share on LinkedIn' product only grants write access.")
        print()
        print("Alternative: use browser-based scraping with Claude Code's Chrome MCP.")
        print("See the docstring at the top of this file for instructions.")
        sys.exit(1)

    if not texts:
        print("No posts found on your profile.")
        sys.exit(0)

    save_posts(texts, output_path)


if __name__ == "__main__":
    main()
