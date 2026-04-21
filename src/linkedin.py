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
REST_BASE = "https://api.linkedin.com/rest"
LINKEDIN_API_VERSION = "202604"  # YYYYMM format required by /rest/ endpoints
REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = "w_member_social openid profile"


def _load_env():
    load_dotenv(ENV_PATH, override=True)


def _get_env(key: str) -> str:
    _load_env()
    value = os.getenv(key, "")
    return value.strip("'\"") if value else ""


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


def check_token_expiry() -> dict:
    """Check how long until the LinkedIn token expires.

    Returns a dict with:
      - expires_at: human-readable expiry date
      - days_remaining: int
      - warning: bool (True if <= 7 days remaining)
    """
    from datetime import datetime

    expiry_str = _get_env("LINKEDIN_TOKEN_EXPIRY")
    if not expiry_str:
        return {"expires_at": "unknown", "days_remaining": -1, "warning": True}

    expiry_ts = int(expiry_str)
    now = int(time.time())
    days = (expiry_ts - now) // 86400
    expires_at = datetime.fromtimestamp(expiry_ts).strftime("%B %d, %Y")

    return {
        "expires_at": expires_at,
        "days_remaining": days,
        "warning": days <= 7,
    }


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {get_valid_token()}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }


def get_profile() -> dict:
    """Fetch the authenticated user's LinkedIn profile."""
    # Try OpenID userinfo endpoint first (works with openid+profile scopes)
    resp = requests.get("https://api.linkedin.com/v2/userinfo", headers=_headers())
    if resp.status_code == 200:
        data = resp.json()
        return {
            "localizedFirstName": data.get("given_name", ""),
            "localizedLastName": data.get("family_name", ""),
            "sub": data.get("sub", ""),
        }
    # Fall back to legacy /me endpoint
    resp = requests.get(f"{API_BASE}/me", headers=_headers())
    resp.raise_for_status()
    return resp.json()


def get_user_urn() -> str:
    """Get the authenticated user's URN (e.g. urn:li:person:abc123)."""
    profile = get_profile()
    # OpenID userinfo returns 'sub', legacy /me returns 'id'
    person_id = profile.get("sub", profile.get("id", ""))
    return f"urn:li:person:{person_id}"


def upload_image(image_source: str) -> str:
    """Upload an image to LinkedIn and return the asset URN.

    Accepts either a local file path or an HTTP(S) URL.

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

    # Step 2: Get image binary (from URL or local file)
    if image_source.startswith(("http://", "https://")):
        dl_resp = requests.get(image_source, timeout=30)
        dl_resp.raise_for_status()
        image_data = dl_resp.content
    else:
        with open(image_source, "rb") as f:
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

    # Try Posts API (current)
    resp = requests.get(
        f"{API_BASE}/posts",
        headers=_headers(),
        params={
            "author": user_urn,
            "q": "author",
            "count": count,
            "sortBy": "LAST_MODIFIED",
        },
    )
    if resp.status_code == 200:
        data = resp.json()
        return data.get("elements", [])

    # Fall back to legacy ugcPosts API
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


def _rest_headers() -> dict:
    """Headers for /rest/ endpoints (Posts API, Documents API)."""
    return {
        "Authorization": f"Bearer {get_valid_token()}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": LINKEDIN_API_VERSION,
    }


def upload_document(document_path: str, title: str = "Document") -> str:
    """Upload a PDF/DOC/PPT to LinkedIn and return the document URN.

    Used for posting carousels (multi-page PDFs render as swipeable carousels).
    Requires w_member_social scope. Max 100MB / 300 pages.
    Supported: PDF, PPT, PPTX, DOC, DOCX.

    Returns:
        Document URN string (e.g. urn:li:document:abc123)
    """
    user_urn = get_user_urn()
    token = get_valid_token()

    # Step 1: Initialize upload
    init_body = {"initializeUploadRequest": {"owner": user_urn}}
    resp = requests.post(
        f"{REST_BASE}/documents?action=initializeUpload",
        headers=_rest_headers(),
        json=init_body,
    )
    resp.raise_for_status()
    init_data = resp.json()["value"]
    upload_url = init_data["uploadUrl"]
    document_urn = init_data["document"]

    # Step 2: Upload the document binary
    if document_path.startswith(("http://", "https://")):
        dl_resp = requests.get(document_path, timeout=60)
        dl_resp.raise_for_status()
        doc_data = dl_resp.content
    else:
        with open(document_path, "rb") as f:
            doc_data = f.read()

    upload_resp = requests.put(
        upload_url,
        headers={"Authorization": f"Bearer {token}"},
        data=doc_data,
    )
    upload_resp.raise_for_status()

    return document_urn


def publish_document_post(text: str, document_urn: str, title: str = "Document") -> dict:
    """Publish a post containing a document (carousel) to LinkedIn.

    Uses the newer /rest/posts API which supports document content.
    Returns the LinkedIn API response including the post ID.
    """
    user_urn = get_user_urn()

    body = {
        "author": user_urn,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "content": {
            "media": {
                "title": title,
                "id": document_urn,
            }
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    resp = requests.post(
        f"{REST_BASE}/posts",
        headers=_rest_headers(),
        json=body,
    )
    resp.raise_for_status()
    return {"id": resp.headers.get("x-restli-id", ""), "status_code": resp.status_code}
