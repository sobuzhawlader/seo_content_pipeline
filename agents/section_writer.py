import json
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential

client = genai.Client()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_gemini_with_retry(prompt: str, mime_type: str = None):
    config = {"response_mime_type": mime_type} if mime_type else {}
    return client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config
    )

def generate_longform_article(brief: dict, live_articles: list[dict]) -> dict:
    sections_html = []
    running_context = ""
    
    # 1. Build Internal Linking Reference List
    links_context = "\n".join([f"- {a['title']}: {a['live_url']}" for a in live_articles if a.get('live_url')])
    if not links_context:
        links_context = "No previous internal articles currently available."

    # 2. Write Compelling Introduction
    intro_prompt = f"""
    Write a comprehensive, engaging introduction for the guide: '{brief['target_keyword']}'.
    - Hook the reader without generic clichés (avoid 'In today's fast-paced world').
    - Clearly outline what key insights the reader will gain.
    - Output strictly semantic HTML with <p> tags.
    """
    intro_html = call_gemini_with_retry(intro_prompt).text
    sections_html.append(intro_html)
    running_context += f"Intro summary: {intro_html[:200]}...\n"

    # 3. Sequentially Write Each H2 Section
    for idx, sec in enumerate(brief.get("sections", [])):
        section_prompt = f"""
        Write Section {idx+1}:
        Heading: {sec['h2']}
        Sub-headings to cover: {sec.get('h3s', [])}
        Key talking points: {sec.get('talking_points', [])}
        Entities to integrate naturally: {sec.get('entities_to_include', [])}
        
        Previous Context: {running_context}
        Available Internal Links to cite if relevant:
        {links_context}
        
        Guidelines:
        - Output semantic HTML with <h2>, <h3>, <p>, <ul>, <li>, or <table> tags.
        - Ensure thorough depth (400-600 words for this section alone).
        - Provide actionable examples, statistics, or step-by-step breakdowns.
        - Naturally hyperlink relevant keywords using the available internal links if appropriate.
        """
        sec_res = call_gemini_with_retry(section_prompt).text
        sections_html.append(sec_res)
        running_context += f"Section '{sec['h2']}' key takeaway: {sec_res[:150]}...\n"

    # 4. Generate FAQ Section & FAQPage Schema
    faq_prompt = f"""
    Write the FAQ section based on these questions: {json.dumps(brief.get('faq_list', []))}.
    Output:
    1. HTML markup for the FAQ section (<h3> for questions, <p> for answers).
    2. Valid Schema.org FAQPage JSON-LD.
    Respond in strict JSON with keys: "faq_html", "schema_json".
    """
    faq_res = call_gemini_with_retry(faq_prompt, mime_type="application/json")
    faq_data = json.loads(faq_res.text)
    sections_html.append(faq_data.get("faq_html", ""))

    full_html = "\n\n".join(sections_html)
    return {
        "content_html": full_html,
        "schema_json": faq_data.get("schema_json", {}),
        "word_count": len(full_html.split())
    }
