import json
from config import get_genai_client
from tenacity import retry, stop_after_attempt, wait_exponential

# ----------------- ANTI-AI DETECTION & HUMANIZATION PROTOCOL -----------------
ANTI_AI_HUMANIZER_RULES = """
CRITICAL ANTI-AI DETECTION & HUMANIZATION CONSTRAINTS:
Your writing must bypass modern AI classifiers (Originality.ai, GPTZero, CopyLeaks) by mimicking natural human cognition and practitioner writing patterns.

1. BANNED AI VOCABULARY & CRUTCHES (DO NOT USE ANY OF THESE UNDER ANY CIRCUMSTANCES):
   - Never use: 'delve', 'tapestry', 'testament', 'beacon', 'furthermore', 'moreover', 'embark', 'harness', 'revolutionize', 'game-changer', 'plethora', 'multifaceted', 'in conclusion', 'to sum up', 'in a nutshell', 'navigating', 'fast-paced world', 'paramount', 'demystify', 'seamlessly', 'vital role', 'ever-evolving', 'shed light', 'unlock', 'pivotal', 'crucial', 'foster', 'underscore', 'it is important to remember'.

2. BURSTINESS & RHYTHMIC VARIATION (HIGH BURSTINESS):
   - Heavily randomize sentence lengths. Write a short, blunt 3-to-6 word sentence (e.g. 'That is a mistake.' or 'The numbers tell a different story.'). Follow it immediately with a nuanced 25-to-35 word sentence containing real constraints, em-dashes (—), or parenthetical trade-offs.
   - Avoid monotonic sentence structures where every sentence starts with [Subject] + [Verb].

3. PRACTITIONER AUTHORITY & FIRST-HAND PERSPECTIVE (EEAT):
   - Write from the perspective of an experienced technical practitioner who works in the trenches.
   - Use pragmatic observations: 'In live deployments,', 'The common gotcha here is', 'On paper this looks ideal, but in practice,', 'Here is where most teams get burned:'.

4. NATURAL HUMAN SYNTAX & CONTRACTIONS:
   - Use natural contractions freely ('it’s', 'don’t', 'can’t', 'we’ve', 'won’t'). Rigid uncontracted phrasing is the #1 telltale sign of machine generation.
   - Never write synthetic mini-summaries or wrap-up sentences at the end of H2 sections. End sections directly on a technical point or actionable takeaway.
"""

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
        info_gain = "Focus on practical benchmarks and real-world implementation constraints."
        
    semantic_triples = "\n".join([f"• {triple}" for triple in brief.get("semantic_entity_triples", [])])
    if not semantic_triples:
        semantic_triples = "Maintain clear subject-predicate-object entity relationships."

    # 3. Write Compelling Introduction (100% Humanized Hook)
    intro_prompt = f"""
    You are an elite veteran industry analyst and technical writer.
    Write an authentic, humanized introduction for the comprehensive guide: '{brief['target_keyword']}'.
    
    Core Subject Context:
    - Central Entity: {brief.get('central_entity', brief['target_keyword'])}
    - Search Intent: {brief.get('search_intent', 'Informational')}
    - Key Information Gain Angles to weave in:
    {info_gain}
    
    {ANTI_AI_HUMANIZER_RULES}
    
    Introduction Specifics:
    - Hook the reader immediately with an authentic, grounded observation or counter-intuitive truth.
    - Zero generic fluff or introductory throat-clearing.
    - Clearly establish what practical problem this guide solves.
    - Output strictly semantic HTML with clean <p> tags.
    """
    intro_html = call_gemini_with_retry(intro_prompt, api_key=api_key).text
    sections_html.append(intro_html)
    running_context += f"Intro summary: {intro_html[:200]}...\n"

    # 4. Sequentially Write Each H2 Section with Humanized Burstiness & Information Gain
    for idx, sec in enumerate(brief.get("sections", [])):
        snippet_instruction = ""
        if sec.get("featured_snippet_target"):
            snippet_instruction = f"""
        POSITION ZERO SNIPPET RULE:
        In the very first paragraph immediately after the <h2> heading, provide a crisp, direct 40-50 word answer to capture Google's Featured Snippet:
        Target Guideline: "{sec['featured_snippet_target']}"
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
        
        Information Gain Directives (Beat generic SERP content):
        {info_gain}
        {snippet_instruction}
        {format_instruction}
        
        Previous Context: {running_context}
        Available Internal Links to naturally hyperlink if relevant:
        {links_context}
        
        {ANTI_AI_HUMANIZER_RULES}
        
        Depth & Style Guidelines:
        - Output strictly semantic HTML with <h2>, <h3>, <p>, <ul>, <ol>, <li>, <table> tags.
        - Ensure 450–650 words of technical depth for this section alone.
        - Include concrete examples, benchmarks, formulas, or troubleshooting solutions.
        - Use high burstiness (mix punchy short sentences with explanatory deep sentences).
        - Hyperlink relevant anchor keywords naturally if they match available internal links.
        - DO NOT write a synthetic wrap-up or conclusion sentence at the end of this section.
        """
        sec_res = call_gemini_with_retry(section_prompt, api_key=api_key).text
        sections_html.append(sec_res)
        running_context += f"Section '{sec['h2']}' key takeaway: {sec_res[:150]}...\n"

    # 5. Generate FAQ Section & FAQPage Schema (Humanized, Direct Q&A)
    faq_prompt = f"""
    Write a concise, humanized FAQ section based on these questions: {json.dumps(brief.get('faq_list', []))}.
    Next Logical Query to optionally address: {brief.get('next_logical_query', 'N/A')}.
    
    {ANTI_AI_HUMANIZER_RULES}
    
    Output:
    1. Semantic HTML markup for the FAQ section (<h3> for questions, <p> for direct, non-robotic answers).
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
