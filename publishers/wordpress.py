import requests
from typing import Optional
from publishers.base import BasePublisher

class WordPressPublisher(BasePublisher):
    def __init__(self, wp_url: str, username: str, app_password: str):
        self.wp_url = wp_url.rstrip("/")
        self.auth = (username, app_password)
        self.posts_endpoint = f"{self.wp_url}/wp-json/wp/v2/posts"

    def publish(
        self,
        title: str,
        content_html: str,
        meta_desc: str,
        focus_kw: str,
        featured_media_id: Optional[int] = None,
        status: str = "draft"
    ) -> str:
        payload = {
            "title": title,
            "content": content_html,
            "status": status,
            "meta": {
                "_yoast_wpseo_metadesc": meta_desc,
                "_yoast_wpseo_focuskw": focus_kw,
                "rank_math_title": title,
                "rank_math_description": meta_desc,
                "rank_math_focus_keyword": focus_kw
            }
        }
        if featured_media_id:
            payload["featured_media"] = featured_media_id

        res = requests.post(self.posts_endpoint, json=payload, auth=self.auth)
        res.raise_for_status()
        data = res.json()
        return data.get("link", "")
