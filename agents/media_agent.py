import os
import requests
from typing import Tuple, Optional

class MediaAgent:
    @staticmethod
    def upload_to_wordpress_media(
        wp_url: str,
        username: str,
        app_pass: str,
        image_bytes: bytes,
        filename: str,
        alt_text: str
    ) -> int:
        """Uploads binary image to WordPress Media Library and sets alt text. Returns media ID."""
        endpoint = f"{wp_url.rstrip('/')}/wp-json/wp/v2/media"
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "image/jpeg"
        }
        res = requests.post(endpoint, data=image_bytes, headers=headers, auth=(username, app_pass))
        res.raise_for_status()
        media_id = res.json()["id"]

        # Update Alt Text & Title
        meta_update = {
            "alt_text": alt_text,
            "title": alt_text
        }
        requests.post(f"{endpoint}/{media_id}", json=meta_update, auth=(username, app_pass))
        return media_id

    @staticmethod
    def fetch_unsplash_image(query: str, client_id: str) -> Tuple[Optional[bytes], str]:
        """Fetches high-quality editorial image from Unsplash API."""
        if not client_id:
            return None, ""
        url = "https://api.unsplash.com/search/photos"
        params = {"query": query, "per_page": 1, "orientation": "landscape"}
        headers = {"Authorization": f"Client-ID {client_id}"}
        try:
            res = requests.get(url, params=params, headers=headers).json()
            if res.get("results"):
                photo = res["results"][0]
                img_res = requests.get(photo["urls"]["regular"])
                alt = photo.get("alt_description") or query
                return img_res.content, alt
        except Exception:
            pass
        return None, ""
