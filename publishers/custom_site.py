import requests
from typing import Optional, Dict, Any
from publishers.base import BasePublisher

class CustomSitePublisher(BasePublisher):
    def __init__(self, webhook_url: str, api_secret: Optional[str] = None):
        self.webhook_url = webhook_url
        self.api_secret = api_secret

    def publish(self, payload: Dict[str, Any]) -> str:
        headers = {"Content-Type": "application/json"}
        if self.api_secret:
            headers["Authorization"] = f"Bearer {self.api_secret}"
        
        res = requests.post(self.webhook_url, json=payload, headers=headers)
        res.raise_for_status()
        data = res.json()
        return data.get("url", "Webhook Delivered Successfully")
