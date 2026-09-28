import os
import requests
from typing import Dict, Any

class SerpResearchAgent:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("SERPER_API_KEY")
        self.endpoint = "https://google.serper.dev/search"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

    def fetch_serp_intelligence(self, query: str) -> Dict[str, Any]:
        if not self.api_key:
            # Fallback mock for testing or when key not yet provided
            return {
                "query": query,
                "top_competitors": [
                    {"title": f"Complete Guide to {query}", "link": "https://example.com/guide", "snippet": f"Comprehensive insights on {query}...", "position": 1}
                ],
                "people_also_ask": [f"What is {query}?", f"How does {query} work?", f"Best practices for {query}?"],
                "related_searches": [f"{query} tips", f"{query} tutorial", f"{query} tools"]
            }

        payload = {"q": query, "gl": "us", "hl": "en", "num": 10}
        response = requests.post(self.endpoint, json=payload, headers=self.headers)
        response.raise_for_status()
        data = response.json()

        organic_results = [
            {
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet"),
                "position": item.get("position")
            }
            for item in data.get("organic", [])[:7]
        ]
        
        paa_questions = [item.get("question") for item in data.get("peopleAlsoAsk", [])]
        related_searches = [item.get("query") for item in data.get("relatedSearches", [])]

        return {
            "query": query,
            "top_competitors": organic_results,
            "people_also_ask": paa_questions,
            "related_searches": related_searches
        }
