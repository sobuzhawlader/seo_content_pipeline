import json
from typing import Dict, Any
from config import get_genai_client
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def build_topical_cluster_map(seed_niche: str, api_key: str = None) -> Dict[str, Any]:
    """
    Generates a production-grade Topical Authority Map based on the exact
    Holistic Semantic SEO methodology pioneered by Koray Tuğberk Gübür and refined by Behzad Mirzapour.
    
    Key Methodology Components:
    1. Central Entity & Source Context definition.
    2. Tri-Tier Topical Hierarchy: Core Section (Commercial), Outer Section (Informational), and Contextual Bridge.
    3. Attribute-based entity decomposition (Components, Types, Methodologies, Pitfalls).
    4. Strict Semantic Internal Linking Matrix (Parent-Child, Sibling-Sibling) with exact anchor text rules.
    5. Keyword Cannibalization Prevention with clear search intent boundaries.
    """
    client = get_genai_client(api_key)
    prompt = f"""
    You are an elite Semantic SEO Architect trained in the Holistic SEO & Topical Authority framework of Koray Tuğberk Gübür and Behzad Mirzapour.
    
    Create an exhaustive, mathematically sound Semantic Topical Map for the Seed Niche: "{seed_niche}".
    
    METHODOLOGY GUIDELINES (BEHZAD MIRZAPOUR / KORAY TUĞBERK GÜBÜR PROCESS):
    1. Identify the **Central Entity** and determine the **Source Context** (the authoritative angle/lens of the domain).
    2. Map out the Tri-Tier Semantic Architecture:
       - **Core Section (Pillar)**: Definitive entity foundation with transactional/commercial intent relevance.
       - **Outer Section (Informational Clusters)**: Foundational definitions, concepts, and theoretical coverage.
       - **Contextual Bridge Clusters**: Procedural guides, comparisons, and troubleshooting linking outer concepts to the core entity.
    3. Decompose topics by **Entity Attributes** (e.g. Types, Techniques, Components, Metrics, Troubleshooting).
    4. Provide strict **Internal Linking Anchors** (Source Context Anchors) between Pillar, Clusters, and Siblings to establish an unbreakable link graph.
    5. Ensure **Zero Cannibalization** by giving each node a mutually exclusive search intent boundary.

    Return strict JSON adhering to this exact schema:
    {{
        "niche": "{seed_niche}",
        "central_entity": "Primary entity name (e.g. Technical SEO)",
        "source_context": "The specific authoritative perspective of the site (e.g. Enterprise SEO Consulting)",
        "pillar_page": {{
            "title": "Comprehensive Pillar Page Title",
            "search_intent": "Informational / Commercial Investigation",
            "primary_keyword": "Primary seed keyword",
            "semantic_definition": "Brief 1-sentence definition of the core entity node",
            "target_word_count": 3500
        }},
        "clusters": [
            {{
                "title": "Complete Cluster Title",
                "tier": "Core / Outer / Contextual Bridge",
                "attribute_focus": "Type / Methodology / Component / Troubleshooting / Comparison",
                "target_subtopic": "Subtopic keyword",
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
