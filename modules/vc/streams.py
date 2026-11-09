"""
Fetches playable audio/video files via BabyAPI / ArtistBots API.
"""
import aiohttp
from config import BASE_URL, API_KEY


async def get_result(query: str, video: bool = False) -> dict:
    """
    Returns a dict with at least: title, url (streamable), duration, video (bool)
    Raises Exception on failure.
    """
    params = {
        "query": query,
        "video": str(video).lower(),
    }
    if API_KEY:
        params["key"] = API_KEY

    url = f"{BASE_URL.rstrip('/')}/song" if not video else f"{BASE_URL.rstrip('/')}/video"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=30) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"API returned {resp.status}: {text[:200]}")
            data = await resp.json()

    if "url" in data:
        return {
            "title": data.get("title") or data.get("name") or query,
            "url": data["url"],
            "duration": data.get("duration", 0),
            "video": video,
            "thumbnail": data.get("thumbnail") or data.get("thumb"),
        }
    if "result" in data and isinstance(data["result"], dict):
        r = data["result"]
        return {
            "title": r.get("title") or query,
            "url": r.get("url") or r.get("link"),
            "duration": r.get("duration", 0),
            "video": video,
            "thumbnail": r.get("thumbnail"),
        }
    raise Exception(f"Unexpected API response: {str(data)[:200]}")
