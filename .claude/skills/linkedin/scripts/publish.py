#!/usr/bin/env python3
"""Publish a post to LinkedIn.

Reads a post from the history by ID, uploads any attached image,
publishes to LinkedIn, and updates the history record.

Usage:
    python .claude/skills/linkedin/scripts/publish.py <post_id>
    python .claude/skills/linkedin/scripts/publish.py --next
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.history import get_post, get_next_scheduled, update_post
from src.linkedin import (
    publish_post,
    publish_document_post,
    upload_image,
    upload_document,
    get_valid_token,
)


def publish(post_id: str) -> dict:
    """Publish a post by ID. Returns the result dict.

    Routes by format:
      - carousel: uploads PDF as a document, posts via /rest/posts
      - single_image / quote_card: uploads image, posts via /v2/ugcPosts
      - text: posts text-only via /v2/ugcPosts
    """
    post = get_post(post_id)
    if not post:
        return {"success": False, "error": f"Post {post_id} not found"}

    if post["status"] == "published":
        return {"success": False, "error": f"Post {post_id} is already published"}

    # Ensure valid token
    try:
        get_valid_token()
    except Exception as e:
        update_post(post_id, status="failed", error=str(e))
        return {"success": False, "error": f"Token error: {e}"}

    fmt = post.get("format", "text")
    image_url = post.get("image_url", "").strip()
    text = post["generated_content"]
    now = datetime.now(timezone.utc).isoformat()

    # === Carousel flow: PDF document upload ===
    if fmt == "carousel" and image_url:
        is_url = image_url.startswith(("http://", "https://"))
        is_local = not is_url and Path(image_url).exists()
        if not (is_url or is_local):
            update_post(post_id, status="failed", error=f"Carousel PDF not found: {image_url}")
            return {"success": False, "error": f"Carousel PDF not found: {image_url}"}

        try:
            doc_urn = upload_document(image_url, title=post.get("topic", "Document")[:100])
        except Exception as e:
            update_post(post_id, status="failed", error=f"Document upload failed: {e}")
            return {"success": False, "error": f"Document upload failed: {e}"}

        try:
            result = publish_document_post(text, doc_urn, title=post.get("topic", "Document")[:100])
            linkedin_id = result.get("id", "")
            update_post(
                post_id,
                status="published",
                linkedin_post_id=linkedin_id,
                published_at=now,
                error="",
            )
            return {"success": True, "linkedin_post_id": linkedin_id}
        except Exception as e:
            update_post(post_id, status="failed", error=str(e))
            return {"success": False, "error": str(e)}

    # === Image/text flow: ugcPosts API ===
    image_asset = ""
    if image_url:
        is_url = image_url.startswith(("http://", "https://"))
        is_local = not is_url and Path(image_url).exists()
        if is_url or is_local:
            try:
                image_asset = upload_image(image_url)
            except Exception as e:
                update_post(post_id, status="failed", error=f"Image upload failed: {e}")
                return {"success": False, "error": f"Image upload failed: {e}"}

    try:
        result = publish_post(text, image_asset)
        linkedin_id = result.get("id", "")
        update_post(
            post_id,
            status="published",
            linkedin_post_id=linkedin_id,
            published_at=now,
            error="",
        )
        return {"success": True, "linkedin_post_id": linkedin_id}
    except Exception as e:
        update_post(post_id, status="failed", error=str(e))
        return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Publish a LinkedIn post")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("post_id", nargs="?", help="Post ID to publish")
    group.add_argument("--next", action="store_true", help="Publish the next scheduled post")

    args = parser.parse_args()

    if args.next:
        post = get_next_scheduled()
        if not post:
            print("No scheduled posts due for publishing.")
            sys.exit(0)
        post_id = post["id"]
        print(f"Next scheduled post: {post_id} (date: {post['scheduled_date']})")
    else:
        post_id = args.post_id

    result = publish(post_id)
    if result["success"]:
        print(f"Published successfully. LinkedIn post ID: {result['linkedin_post_id']}")
    else:
        print(f"Failed to publish: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
