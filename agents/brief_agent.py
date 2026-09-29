import json
from config import get_genai_client
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_content_brief(topic: str, serp_intel: dict, api_key: str = None) -> dict:
    """
    Generates an enterprise-grade Semantic & Information-Gain Content Brief
    based on Koray Tuğberk Gübür and Behzad Hussain's methodology.
    
    Key Features:
    1. Competitor Gap Analysis (Information Gain Patent compliance).
    2. Entity Salience & Semantic Triples (Subject-Predicate-Object).
    3. Featured Snippet Baiting (40-50 word direct answer definitions).
    4. Format Directives (Comparison Tables, Structured Lists).
    5. User Search Journey & Next Logical Query mapping.
    """
    client = get_genai_client(api_key)
    prompt = f"""
    You are an elite Semantic SEO Content Architect trained in the Information-Gain & Holistic SEO Framework of Koray Tuğberk Gübür and Behzad Hussain.
    
    Create an exhaustive, high-authority Content Brief for the topic: "{topic}".
    
    LIVE SERP COMPETITOR INTELLIGENCE:
    - Top Competitor Snippets: {json.dumps(serp_intel.get('top_competitors', []))}
    - People Also Ask (PAA) Questions: {json.dumps(serp_intel.get('people_also_ask', []))}
    - Related Search Queries: {json.dumps(serp_intel.get('related_searches', []))}
    
    BRIEF ARCHITECTURE INSTRUCTIONS:
    1. **Information Gain Angles**: Identify 3-4 specific high-value angles, metrics, benchmarks, or real-world nuances that the top 7 competitors completely MISSED or covered superficially.
    2. **Semantic Entity Triples**: Formulate 4-6 explicit Subject-Predicate-Object semantic relationships that must be integrated to satisfy Google's Knowledge Graph.
    3. **User Search Journey**: Identify the user's "Next Logical Query" to resolve their entire problem without bouncing back to SERP.
    4. **Featured Snippet Bait**: For the core conceptual H2 sections, define a 40-50 word direct answer guideline to capture Position Zero.
    5. **Format Directives**: Explicitly designate sections that require a Markdown/HTML Comparison Table, Step-by-Step Breakdown, or Bulleted List.
    6. **Entities**: Define high-salience secondary entities for each section.
    
    Return strict JSON adhering to this exact schema:
    {{
        "target_keyword": "{topic}",
        "central_entity": "Primary entity node (e.g. Vector Database)",
        "search_intent": "Informational / Commercial Investigation / Procedural",
        "recommended_word_count": 2800,
        "meta_description": "Compelling 150-160 character meta description featuring the primary entity and value hook.",
        "information_gain_angles": [
            "Specific competitor gap 1 (e.g. Real-world latency benchmark under 10M vectors)",
            "Specific competitor gap 2 (e.g. Hidden cost comparison table of cloud vs self-hosted)"
        ],
        "semantic_entity_triples": [
            "[Subject Entity] --(Predicate Relationship)--> [Object Entity]"
        ],
        "next_logical_query": "Next search query the user will logically seek after this",
        "sections": [
            {{
                "h2": "Comprehensive heading title",
                "h3s": ["Subheading A", "Subheading B"],
                "talking_points": ["Specific deep point 1", "Specific deep point 2"],
                "entities_to_include": ["Entity1", "Entity2", "Entity3"],
                "format_directive": "prose / comparison_table / step_by_step_list / pros_cons_box",
                "featured_snippet_target": "Direct 40-50 word crisp answer blueprint to place immediately under the H2"
            }}
        ],
        "faq_list": [
            {{"question": "PAA Question text", "answer_guideline": "Direct 2-3 sentence answer points"}}
        ]
    }}
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)
