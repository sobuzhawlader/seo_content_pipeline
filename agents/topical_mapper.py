import json
from typing import Dict, Any
from config import get_genai_client
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def build_topical_cluster_map(seed_niche: str, api_key: str = None) -> Dict[str, Any]:
    """Generates a comprehensive pillar and cluster topical map for establishing topical authority."""
    client = get_genai_client(api_key)
    prompt = f"""
    You are an elite SEO Strategist specializing in Topical Authority and Semantic Clustering.
    Generate a complete Pillar-and-Cluster topical hierarchy for the seed niche: "{seed_niche}".
    
    Requirements:
    1. Identify 1 core Pillar Page topic that comprehensively covers the niche foundation.
    2. Identify 4 to 6 supporting Cluster Topics that delve deep into subtopics.
    3. Suggest internal linking arrows (which clusters link to pillar and each other).
    
    Return strict JSON with this schema:
    {{
        "niche": "{seed_niche}",
        "pillar_page": {{
            "title": "Comprehensive Title",
            "search_intent": "Informational",
            "primary_keyword": "keyword"
        }},
        "clusters": [
            {{
                "title": "Cluster Article Title",
                "target_subtopic": "Subtopic name",
                "relationship": "supporting pillar",
                "anchor_text_suggestion": "anchor"
            }}
        ]
    }}
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)
