#!/usr/bin/env python3
"""Generate an HTML preview of a LinkedIn post.

Renders a LinkedIn-style post card with the correct image position,
text truncation with "see more" toggle, and action bar.

Usage:
    python .claude/skills/linkedin/scripts/preview_post.py <post_id>
    python .claude/skills/linkedin/scripts/preview_post.py <post_id> --open
"""

import argparse
import html
import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.history import get_post

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Post Preview — {scheduled_date}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background: #f3f2ef;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      display: flex;
      justify-content: center;
      padding: 40px 20px;
    }}

    .feed {{ width: 100%; max-width: 555px; }}

    .preview-label {{
      text-align: center;
      font-size: 11px;
      color: #999;
      margin-bottom: 12px;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }}

    .card {{
      background: #fff;
      border-radius: 8px;
      border: 1px solid #e0e0e0;
      overflow: hidden;
    }}

    /* Header */
    .card-header {{
      display: flex;
      align-items: flex-start;
      padding: 12px 16px 0;
      gap: 8px;
    }}

    .avatar {{
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: linear-gradient(135deg, #0a66c2, #004182);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 18px;
      font-weight: 700;
      flex-shrink: 0;
    }}

    .author-info {{ flex: 1; }}

    .author-name {{
      font-size: 14px;
      font-weight: 600;
      color: rgba(0,0,0,0.9);
      line-height: 1.3;
    }}

    .author-headline {{
      font-size: 12px;
      color: rgba(0,0,0,0.6);
      line-height: 1.3;
      margin-top: 1px;
    }}

    .post-meta {{
      font-size: 12px;
      color: rgba(0,0,0,0.6);
      margin-top: 2px;
    }}

    .follow-btn {{
      font-size: 14px;
      font-weight: 600;
      color: #0a66c2;
      background: none;
      border: none;
      cursor: pointer;
      flex-shrink: 0;
      align-self: center;
    }}

    /* Post text */
    .post-text-wrap {{
      padding: 8px 16px 4px;
      font-size: 14px;
      color: rgba(0,0,0,0.9);
      line-height: 1.5;
    }}

    .post-text {{
      white-space: pre-wrap;
      overflow: hidden;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
    }}

    .post-text.expanded {{
      display: block;
      -webkit-line-clamp: unset;
    }}

    .see-more {{
      color: rgba(0,0,0,0.6);
      cursor: pointer;
      font-size: 14px;
      padding: 0 16px 10px;
      display: block;
    }}

    .see-more:hover {{ text-decoration: underline; }}

    /* Image */
    .post-image {{
      width: 100%;
      display: block;
      max-height: 415px;
      object-fit: cover;
    }}

    /* Quote card overlay */
    .quote-card-wrap {{
      position: relative;
      width: 100%;
    }}

    .quote-card-wrap .post-image {{
      max-height: 415px;
    }}

    /* Reactions bar */
    .reactions-bar {{
      padding: 6px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid #e0e0e0;
    }}

    .reaction-counts {{
      font-size: 12px;
      color: rgba(0,0,0,0.6);
    }}

    /* Action buttons */
    .action-bar {{
      display: flex;
      padding: 2px 8px;
    }}

    .action-btn {{
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 10px 4px;
      font-size: 13px;
      font-weight: 600;
      color: rgba(0,0,0,0.6);
      background: none;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }}

    .action-btn:hover {{ background: #f3f2ef; color: rgba(0,0,0,0.9); }}

    /* Format badge */
    .format-badge {{
      display: inline-block;
      font-size: 10px;
      font-weight: 600;
      background: #e8f0fe;
      color: #0a66c2;
      border-radius: 4px;
      padding: 2px 6px;
      margin-left: 6px;
      text-transform: uppercase;
      letter-spacing: 0.4px;
      vertical-align: middle;
    }}

    .no-image-note {{
      padding: 16px;
      background: #f9f9f9;
      border-top: 1px dashed #ddd;
      font-size: 12px;
      color: #999;
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="feed">
    <div class="preview-label">
      Post Preview — {scheduled_date}
      <span class="format-badge">{format}</span>
    </div>
    <div class="card">

      <div class="card-header">
        <div class="avatar">KT</div>
        <div class="author-info">
          <div class="author-name">Kerri Turski (she/her)</div>
          <div class="author-headline">Principal Architect | Technical Product Management | AWS Certified</div>
          <div class="post-meta">Just now · 🌐</div>
        </div>
        <button class="follow-btn">+ Follow</button>
      </div>

      <div class="post-text-wrap">
        <div class="post-text" id="postText">{post_content}</div>
      </div>
      <span class="see-more" id="seeMore" onclick="
        const t = document.getElementById('postText');
        const s = document.getElementById('seeMore');
        if (t.classList.contains('expanded')) {{
          t.classList.remove('expanded');
          s.textContent = '…see more';
        }} else {{
          t.classList.add('expanded');
          s.textContent = 'see less';
        }}
      ">…see more</span>

      {image_section}

      <div class="reactions-bar">
        <div class="reaction-counts">Be the first to react</div>
        <div style="font-size:12px; color:rgba(0,0,0,0.6);">0 comments</div>
      </div>

      <div class="action-bar">
        <button class="action-btn">👍 Like</button>
        <button class="action-btn">💬 Comment</button>
        <button class="action-btn">🔁 Repost</button>
        <button class="action-btn">📤 Send</button>
      </div>

    </div>
  </div>
</body>
</html>"""

IMAGE_SECTION = """<img class="post-image" src="{image_url}" alt="Post image" />"""

NO_IMAGE_SECTION = """<div class="no-image-note">No image attached — text-only post</div>"""


def format_content_as_html(text: str) -> str:
    """Convert plain post text to HTML-safe content with hashtag and URL linking."""
    import re
    # Only escape < > & but preserve quotes and apostrophes
    escaped = html.escape(text, quote=False)
    # Link hashtags first (only matches # followed by a letter, not hex codes)
    escaped = re.sub(
        r'#([A-Za-z]\w*)',
        r'<span style="color:#0a66c2">#\1</span>',
        escaped
    )
    # Auto-link URLs (after hashtags to avoid corrupting href attributes)
    escaped = re.sub(
        r'(https?://[^\s<]+)',
        r'<a href="\1" style="color:#0a66c2;text-decoration:none" target="_blank">\1</a>',
        escaped
    )
    return escaped


def generate_preview(post_id: str) -> Path:
    post = get_post(post_id)
    if not post:
        print(f"ERROR: Post {post_id} not found.")
        sys.exit(1)

    content_html = format_content_as_html(post.get("generated_content", ""))
    image_url = post.get("image_url", "").strip()
    fmt = post.get("format", "text")
    scheduled = post.get("scheduled_date", "")

    if image_url:
        image_section = IMAGE_SECTION.format(image_url=image_url)
    else:
        image_section = NO_IMAGE_SECTION

    rendered = HTML_TEMPLATE.format(
        scheduled_date=scheduled,
        format=fmt,
        post_content=content_html,
        image_section=image_section,
    )

    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"preview-{post_id[:8]}.html"
    output_path.write_text(rendered)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate HTML preview of a LinkedIn post")
    parser.add_argument("post_id", help="Post ID from data/posts.tsv")
    parser.add_argument("--open", action="store_true", help="Open preview in browser after generating")
    args = parser.parse_args()

    path = generate_preview(args.post_id)
    print(f"Preview generated: {path}")

    if args.open:
        subprocess.run(["open", str(path)])


if __name__ == "__main__":
    main()
