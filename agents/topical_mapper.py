import json
from typing import Dict, Any
from config import get_genai_client
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def build_topical_cluster_map(seed_niche: str, api_key: str = None) -> Dict[str, Any]:
    """
    Generates an enterprise-grade Topical Authority Map based on the exact
    Semantic SEO framework of Koray Tuğberk Gübür and his prominent Pakistani student/practitioner
    Behzad Hussain (Founder of Rank Brilliance).
    
    Core Components of Behzad Hussain's Koray Framework Implementation:
    1. Central Entity & Source Context definition (Establishing authoritative domain angle).
    2. Core Section vs. Outer Section division (Monetization Core vs. Informational Trust clusters).
    3. Contextual Bridge Nodes connecting informational discovery to the core commercial entity.
    4. Lexical Path & Attribute Decomposition (Components, Types, Methodologies, Pitfalls).
    5. Strict Semantic Internal Linking Matrix (Parent-Child, Sibling-Sibling) with exact anchor text rules.
    6. URL slug structure design and Cannibalization Guard.
    """
    client = get_genai_client(api_key)
    prompt = f"""
    You are an elite Semantic SEO Engineer trained strictly in the Topical Authority Framework of Koray Tuğberk Gübür and Behzad Hussain (Rank Brilliance, Pakistan).
    
    Construct a mathematically sound, complete Semantic Topical Map for the Seed Niche: "{seed_niche}".
    
    FRAMEWORK RULES (BEHZAD HUSSAIN / KORAY TUĞBERK GÜBÜR):
    1. **Central Entity**: Define the primary semantic node representing the topic.
    2. **Source Context**: Define the exact operational lens and expertise angle of the domain.
    3. **Core Section (Pillar)**: The central commercial/monetization entity foundation.
    4. **Outer Section (Informational Trust Clusters)**: Definitions, concepts, underlying mechanics, and background context.
    5. **Contextual Bridges**: How-tos, comparisons, troubleshooting, and workflows bridging Outer informational trust to Core conversion.
    6. **Lexical Path & URL Structure**: Clean hierarchical URL slugs avoiding keyword overlap.
    7. **Anchor Text Directionality**: Explicit internal linking anchor text rules (Outbound to Pillar, Inbound, and Sibling Cross-links).
    8. **Zero Cannibalization**: Mutually exclusive search intents.

    Return strict JSON matching this exact schema:
    {{
        "niche": "{seed_niche}",
        "central_entity": "Primary entity name (e.g. Technical SEO)",
        "source_context": "The specific authoritative angle (e.g. Enterprise SEO Consulting)",
        "pillar_page": {{
            "title": "Comprehensive Core Pillar Page Title",
            "search_intent": "Informational / Commercial Investigation",
            "primary_keyword": "Primary seed keyword",
            "url_slug": "/core-slug",
            "semantic_definition": "Brief 1-sentence definition of the core entity node",
            "target_word_count": 3500
        }},
        "clusters": [
            {{
                "title": "Complete Cluster Title",
                "tier": "Core / Outer / Contextual Bridge",
                "attribute_focus": "Type / Methodology / Component / Troubleshooting / Comparison",
                "target_subtopic": "Subtopic keyword",
                "url_slug": "/parent/cluster-slug",
                "search_intent": "Informational / Commercial",
                "inbound_anchor_text": "Exact anchor text this article should receive from other articles",
                "outbound_anchor_text": "Exact anchor text this article must use to link back to the Pillar",
                "sibling_link_suggestion": "Suggested title of another cluster in this list to link to"
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
