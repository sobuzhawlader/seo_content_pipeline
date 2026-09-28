import json
from config import get_genai_client
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_content_brief(topic: str, serp_intel: dict, api_key: str = None) -> dict:
    client = get_genai_client(api_key)
    prompt = f"""
    You are an expert Content Strategist & Semantic SEO Specialist.
    Create an exhaustive, data-driven Content Brief for the topic: "{topic}".
    
    Incorporate this live SERP Intelligence:
    - Competitor Snippets: {json.dumps(serp_intel.get('top_competitors', []))}
    - People Also Ask (PAA): {json.dumps(serp_intel.get('people_also_ask', []))}
    - Related Searches: {json.dumps(serp_intel.get('related_searches', []))}
    
    Return strict JSON with the following structure:
    {{
        "target_keyword": "{topic}",
        "search_intent": "informational / commercial",
        "recommended_word_count": 2500,
        "meta_description": "Compelling 150-160 character meta description with target keyword.",
        "sections": [
            {{
                "h2": "Comprehensive heading title",
                "h3s": ["Subheading A", "Subheading B"],
                "talking_points": ["Specific point 1", "Specific point 2"],
                "entities_to_include": ["Entity1", "Entity2"]
            }}
        ],
        "faq_list": [
            {{"question": "Question text from PAA", "answer_guideline": "Brief points"}}
        ]
    }}
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)
