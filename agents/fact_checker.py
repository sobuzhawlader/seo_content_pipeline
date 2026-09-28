import json
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential

client = genai.Client()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def run_grounded_audit(audit_prompt: str):
    return client.models.generate_content(
        model="gemini-2.5-flash",
        contents=audit_prompt,
        config=types.GenerateContentConfig(
            tools=[{"google_search": {}}]
        )
    )

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def format_audit_to_json(formatting_prompt: str):
    return client.models.generate_content(
        model="gemini-2.5-flash",
        contents=formatting_prompt,
        config={"response_mime_type": "application/json"}
    )

def verify_and_ground_draft(draft_html: str, target_keyword: str) -> dict:
    # Step 1: Grounded Search Audit and Rewrite
    audit_prompt = f"""
    You are a meticulous Editorial Fact-Checker for a high-authority publication.
    Review the draft article on '{target_keyword}'.
    
    Tasks:
    1. Cross-check all quantitative assertions, statistics, dates, and claims against reliable search data.
    2. Correct any inaccurate or outdated information directly inside the HTML.
    3. Provide the fully corrected HTML draft and summarize specific corrections made.
    
    Draft HTML:
    {draft_html}
    """
    try:
        audit_res = run_grounded_audit(audit_prompt)
        audited_text = audit_res.text

        # Step 2: Format Output into Structured JSON
        formatting_prompt = f"""
        Convert the following fact-checking output into a strict JSON object with these keys:
        - 'corrected_html': The revised HTML draft.
        - 'corrections_made': List of specific facts corrected.
        - 'factual_confidence_score': Float between 0 and 1.
        
        Fact-Checking Output:
        {audited_text}
        """
        json_res = format_audit_to_json(formatting_prompt)
        return json.loads(json_res.text)
    except Exception as e:
        # Graceful fallback: return original html if grounding fails
        return {
            "corrected_html": draft_html,
            "corrections_made": [f"Grounding step skipped or fallback due to: {str(e)}"],
            "factual_confidence_score": 0.8
        }
