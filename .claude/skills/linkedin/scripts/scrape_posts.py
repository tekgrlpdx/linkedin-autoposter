#!/usr/bin/env python3
"""Scrape the user's own LinkedIn posts for persona building.

Fetches recent posts via the LinkedIn API and saves the text content
to samples/linkedin_posts.txt for use as writing style reference.

Usage:
    python .claude/skills/linkedin/scripts/scrape_posts.py [--count 20]
"""

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.linkedin import get_user_posts


def extract_post_text(post: dict) -> str:
    """Extract the text content from a LinkedIn API post object."""
    specific = post.get("specificContent", {})
    share = specific.get("com.linkedin.ugc.ShareContent", {})
    commentary = share.get("shareCommentary", {})
    return commentary.get("text", "")


def main():
    parser = argparse.ArgumentParser(description="Scrape your LinkedIn posts for persona building")
    parser.add_argument("--count", type=int, default=20, help="Number of posts to fetch")
    args = parser.parse_args()

    print(f"Fetching your {args.count} most recent LinkedIn posts...")

    try:
        posts = get_user_posts(count=args.count)
    except Exception as e:
        print(f"ERROR: Failed to fetch posts: {e}")
        sys.exit(1)

    if not posts:
        print("No posts found on your profile.")
        sys.exit(0)

    texts = []
    for post in posts:
        text = extract_post_text(post)
        if text.strip():
            texts.append(text.strip())

    if not texts:
        print("Posts found but none had text content.")
        sys.exit(0)

    # Write to samples directory
    output_path = project_root / "samples" / "linkedin_posts.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        for i, text in enumerate(texts):
            if i > 0:
                f.write("\n\n---\n\n")
            f.write(text)

    print(f"Saved {len(texts)} posts to {output_path}")
    print("These will be used as writing style reference when generating new posts.")


if __name__ == "__main__":
    main()
