"""LinkedIn API integration.

Handles OAuth 2.0 authentication, token refresh, and post publishing
for personal LinkedIn profiles.
"""

import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv, set_key

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

AUTHORIZE_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
API_BASE = "https://api.linkedin.com/v2"
REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = "w_member_social r_member_social"


def _load_env():
    load_dotenv(ENV_PATH)


def _get_env(key: str) -> str:
    _load_env()
    return os.getenv(key, "")


def _set_env(key: str, value: str):
    if ENV_PATH.exists():
        set_key(str(ENV_PATH), key, value)


def get_authorization_url() -> str:
    """Generate the OAuth 2.0 authorization URL for the user to visit."""
    client_id = _get_env("LINKEDIN_CLIENT_ID")
    if not client_id:
        raise ValueError("LINKEDIN_CLIENT_ID not set in .env")
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
    }
    query = "&".join(f"{k}={requests.utils.quote(v)}" for k, v in params.items())
    return f"{AUTHORIZE_URL}?{query}"


def exchange_code_for_tokens(auth_code: str) -> dict:
    """Exchange an authorization code for access and refresh tokens."""
    resp = requests.post(TOKEN_URL, data={
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": _get_env("LINKEDIN_CLIENT_ID"),
        "client_secret": _get_env("LINKEDIN_CLIENT_SECRET"),
    })
    resp.raise_for_status()
    data = resp.json()

    access_token = data["access_token"]
    refresh_token = data.get("refresh_token", "")
    expires_in = data.get("expires_in", 5184000)  # default 60 days
    expiry = int(time.time()) + expires_in

    _set_env("LINKEDIN_ACCESS_TOKEN", access_token)
    _set_env("LINKEDIN_REFRESH_TOKEN", refresh_token)
    _set_env("LINKEDIN_TOKEN_EXPIRY", str(expiry))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": expires_in,
    }


def refresh_access_token() -> str:
    """Refresh the access token using the refresh token."""
    refresh_token = _get_env("LINKEDIN_REFRESH_TOKEN")
    if not refresh_token:
        raise ValueError(
            "No refresh token available. Run /linkedin setup to re-authenticate."
        )

    resp = requests.post(TOKEN_URL, data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": _get_env("LINKEDIN_CLIENT_ID"),
        "client_secret": _get_env("LINKEDIN_CLIENT_SECRET"),
    })
    resp.raise_for_status()
    data = resp.json()

    access_token = data["access_token"]
    new_refresh = data.get("refresh_token", refresh_token)
    expires_in = data.get("expires_in", 5184000)
    expiry = int(time.time()) + expires_in

    _set_env("LINKEDIN_ACCESS_TOKEN", access_token)
    _set_env("LINKEDIN_REFRESH_TOKEN", new_refresh)
    _set_env("LINKEDIN_TOKEN_EXPIRY", str(expiry))

    return access_token


def get_valid_token() -> str:
    """Get a valid access token, refreshing if expired."""
    token = _get_env("LINKEDIN_ACCESS_TOKEN")
    expiry = _get_env("LINKEDIN_TOKEN_EXPIRY")

    if not token:
        raise ValueError("No access token. Run /linkedin setup first.")

    if expiry and int(expiry) < int(time.time()) + 300:
        token = refresh_access_token()

    return token


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {get_valid_token()}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }


def get_profile() -> dict:
    """Fetch the authenticated user's LinkedIn profile."""
    resp = requests.get(f"{API_BASE}/me", headers=_headers())
    resp.raise_for_status()
    return resp.json()


def get_user_urn() -> str:
    """Get the authenticated user's URN (e.g. urn:li:person:abc123)."""
    profile = get_profile()
    return f"urn:li:person:{profile['id']}"


def upload_image(image_path: str) -> str:
    """Upload an image to LinkedIn and return the asset URN.

    LinkedIn requires a two-step upload:
    1. Register the upload and get an upload URL
    2. PUT the binary image data to that URL
    """
    user_urn = get_user_urn()
    token = get_valid_token()

    # Step 1: Register upload
    register_body = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": user_urn,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent",
                }
            ],
        }
    }
    resp = requests.post(
        f"{API_BASE}/assets?action=registerUpload",
        headers=_headers(),
        json=register_body,
    )
    resp.raise_for_status()
    upload_data = resp.json()

    asset = upload_data["value"]["asset"]
    upload_url = upload_data["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
    ]["uploadUrl"]

    # Step 2: Upload image binary
    with open(image_path, "rb") as f:
        image_data = f.read()

    resp = requests.put(
        upload_url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream",
        },
        data=image_data,
    )
    resp.raise_for_status()

    return asset


def publish_post(text: str, image_asset: str = "") -> dict:
    """Publish a post to the authenticated user's LinkedIn profile.

    Args:
        text: The post body text.
        image_asset: Optional LinkedIn asset URN from upload_image().

    Returns:
        LinkedIn API response including the post ID.
    """
    user_urn = get_user_urn()

    media = []
    if image_asset:
        media.append({
            "status": "READY",
            "description": {"text": "Post image"},
            "media": image_asset,
            "title": {"text": "Post image"},
        })

    body = {
        "author": user_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "IMAGE" if image_asset else "NONE",
                "media": media,
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    resp = requests.post(
        f"{API_BASE}/ugcPosts",
        headers=_headers(),
        json=body,
    )
    resp.raise_for_status()
    return resp.json()


def get_user_posts(count: int = 20) -> list[dict]:
    """Fetch the user's recent LinkedIn posts for persona scraping."""
    user_urn = get_user_urn()
    resp = requests.get(
        f"{API_BASE}/ugcPosts",
        headers=_headers(),
        params={
            "q": "authors",
            "authors": f"List({user_urn})",
            "count": count,
            "sortBy": "LAST_MODIFIED",
        },
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("elements", [])


def get_post_stats(post_urns: list[str]) -> list[dict]:
    """Fetch engagement stats for a list of post URNs.

    Uses the socialMetadata endpoint for personal profile posts.
    LinkedIn's personal profile analytics are limited compared to
    organization pages  - basic engagement counts are available.
    """
    if not post_urns:
        return []

    stats = []
    for urn in post_urns:
        resp = requests.get(
            f"{API_BASE}/socialMetadata/{urn}",
            headers=_headers(),
        )
        if resp.status_code == 200:
            stats.append(resp.json())
    return stats
