"""Stock photo sourcing from Unsplash and Pexels.

Queries free stock photo APIs to find images matching post content.
Returns publicly accessible URLs suitable for uploading to Canva.
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()


def search_unsplash(query: str, count: int = 5) -> list[dict]:
    """Search Unsplash for photos matching a query.

    Returns a list of dicts with: url, thumb_url, description, photographer, download_url.
    """
    api_key = os.getenv("UNSPLASH_ACCESS_KEY", "")
    if not api_key:
        return []

    resp = requests.get(
        "https://api.unsplash.com/search/photos",
        headers={"Authorization": f"Client-ID {api_key}"},
        params={
            "query": query,
            "per_page": count,
            "orientation": "landscape",
        },
    )
    if resp.status_code != 200:
        return []

    results = []
    for photo in resp.json().get("results", []):
        results.append({
            "id": photo["id"],
            "url": photo["urls"]["regular"],
            "thumb_url": photo["urls"]["thumb"],
            "description": photo.get("alt_description", ""),
            "photographer": photo["user"]["name"],
            "download_url": photo["links"]["download"],
        })
    return results


def search_pexels(query: str, count: int = 5) -> list[dict]:
    """Search Pexels for photos matching a query.

    Returns a list of dicts with: url, thumb_url, description, photographer.
    """
    api_key = os.getenv("PEXELS_API_KEY", "")
    if not api_key:
        return []

    resp = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": api_key},
        params={
            "query": query,
            "per_page": count,
            "orientation": "landscape",
        },
    )
    if resp.status_code != 200:
        return []

    results = []
    for photo in resp.json().get("photos", []):
        results.append({
            "id": str(photo["id"]),
            "url": photo["src"]["large"],
            "thumb_url": photo["src"]["small"],
            "description": photo.get("alt", ""),
            "photographer": photo["photographer"],
        })
    return results


def search_photos(query: str, count: int = 5) -> list[dict]:
    """Search for photos using Unsplash first, falling back to Pexels.

    Returns a list of photo dicts from whichever source has results.
    """
    results = search_unsplash(query, count)
    if not results:
        results = search_pexels(query, count)
    return results
