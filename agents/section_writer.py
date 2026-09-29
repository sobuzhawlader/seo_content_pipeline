import json
from config import get_genai_client
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_gemini_with_retry(prompt: str, mime_type: str = None, api_key: str = None):
    client = get_genai_client(api_key)
    config = {"response_mime_type": mime_type} if mime_type else {}
    return client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config
    )

def generate_longform_article(brief: dict, live_articles: list[dict], api_key: str = None) -> dict:
    sections_html = []
    running_context = ""
    
    # 1. Build Internal Linking Reference List
    links_context = "\n".join([f"- {a['title']}: {a['live_url']}" for a in live_articles if a.get('live_url')])
    if not links_context:
        links_context = "No previous internal articles currently available."

    # 2. Extract Semantic & Information Gain Directives
    info_gain = "\n".join([f"• {angle}" for angle in brief.get("information_gain_angles", [])])
    if not info_gain:
        info_gain = "Focus on first-hand analytical depth and concrete numbers."
        
    semantic_triples = "\n".join([f"• {triple}" for triple in brief.get("semantic_entity_triples", [])])
    if not semantic_triples:
        semantic_triples = "Maintain clear subject-predicate-object entity relationships."

    # 3. Write Compelling Introduction (Entity-Centric Hook)
    intro_prompt = f"""
    Write a high-authority, engaging introduction for the comprehensive guide: '{brief['target_keyword']}'.
    
    Core Subject Context:
    - Central Entity: {brief.get('central_entity', brief['target_keyword'])}
    - Search Intent: {brief.get('search_intent', 'Informational')}
    - Key Information Gain Focus:
    {info_gain}
    
    Guidelines:
    - Hook the reader immediately with an analytical or technical reality (STRICTLY avoid clichés like 'In today's fast-paced digital landscape' or 'Have you ever wondered').
    - State clearly what specific answers and advanced breakdowns the reader will unlock.
    - Output strictly semantic HTML with clean <p> tags.
    """
    intro_html = call_gemini_with_retry(intro_prompt, api_key=api_key).text
    sections_html.append(intro_html)
    running_context += f"Intro summary: {intro_html[:200]}...\n"

    # 4. Sequentially Write Each H2 Section with Information-Gain Depth
    for idx, sec in enumerate(brief.get("sections", [])):
        snippet_instruction = ""
        if sec.get("featured_snippet_target"):
            snippet_instruction = f"""
        POSITION ZERO SNIPPET RULE:
        In the very first paragraph immediately after the <h2> heading, provide a crisp, definitive 40-50 word direct answer to capture Google's Featured Snippet:
        Guideline: "{sec['featured_snippet_target']}"
            """

        format_instruction = ""
        fmt = sec.get("format_directive", "prose")
        if fmt == "comparison_table":
            format_instruction = "STRUCTURE DIRECTIVE: Include a comprehensive semantic HTML <table> (with <thead>, <tbody>, <th>, <td>) comparing relevant options, criteria, or metrics."
        elif fmt in ["step_by_step_list", "bulleted_list"]:
            format_instruction = "STRUCTURE DIRECTIVE: Include an organized HTML ordered <ol> or unordered <ul> list with detailed, step-by-step action items."

        section_prompt = f"""
        Write Section {idx+1}:
        Heading: {sec['h2']}
        Sub-headings to cover: {sec.get('h3s', [])}
        Key talking points: {sec.get('talking_points', [])}
        Entities to integrate naturally: {sec.get('entities_to_include', [])}
        
        Semantic Entity Relationships to reinforce:
        {semantic_triples}
        
        Information Gain Directives (Make sure this section beats generic SERP content):
        {info_gain}
        {snippet_instruction}
        {format_instruction}
        
        Previous Context: {running_context}
        Available Internal Links to naturally hyperlink if relevant:
        {links_context}
        
        Depth & Style Guidelines:
        - Output strictly semantic HTML with <h2>, <h3>, <p>, <ul>, <ol>, <li>, <table> tags.
        - Ensure 450–650 words of technical depth for this section alone.
        - Include concrete examples, benchmarks, formulas, or troubleshooting solutions.
        - Hyperlink relevant anchor keywords naturally if they match available internal links.
        """
        sec_res = call_gemini_with_retry(section_prompt, api_key=api_key).text
        sections_html.append(sec_res)
        running_context += f"Section '{sec['h2']}' key takeaway: {sec_res[:150]}...\n"

    # 5. Generate FAQ Section & FAQPage Schema
    faq_prompt = f"""
    Write the FAQ section based on these questions: {json.dumps(brief.get('faq_list', []))}.
    Next Logical Query to optionally address: {brief.get('next_logical_query', 'N/A')}.
    
    Output:
    1. Semantic HTML markup for the FAQ section (<h3> for questions, <p> for direct answers).
    2. Valid Schema.org FAQPage JSON-LD.
    Respond in strict JSON with keys: "faq_html", "schema_json".
    """
    faq_res = call_gemini_with_retry(faq_prompt, mime_type="application/json", api_key=api_key)
    faq_data = json.loads(faq_res.text)
    sections_html.append(faq_data.get("faq_html", ""))

    full_html = "\n\n".join(sections_html)
    return {
        "content_html": full_html,
        "schema_json": faq_data.get("schema_json", {}),
        "word_count": len(full_html.split())
    }
