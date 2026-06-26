import os
import dotenv
from agent_utils.retry_helper import retry_with_backoff

dotenv.load_dotenv()   

_client = None

def _get_client():
    global _client
    if _client is None:
        print("[GEMINI] Initializing Gemini API client lazily...")
        from google import genai
        _client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )
        print("[GEMINI] Gemini API client initialized successfully.")
    return _client

def _is_quota_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return ("resource_exhausted" in msg) or ("quota" in msg) or ("429" in msg) or ("503" in msg) or ("unavailable" in msg)

@retry_with_backoff(max_retries=3, initial_delay=2.0, backoff_factor=2.0)
def _call_gemini_with_retry(prompt):
    client = _get_client()
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )
    return response.text

def generate_cover_letter(resume_text, job):
    """
    Generates a concise, tailored cover letter using Gemini, with retry logic and fallback.
    """
    def _fallback_letter() -> str:
        title = job.get("title", "the role")
        company = job.get("company", "your company")
        return (
            f"Dear Hiring Manager at {company},\n\n"
            f"I’m writing to express my interest in the {title} position. "
            "My experience aligns well with the role, and I’m confident I can contribute value quickly.\n\n"
            "I’d welcome the opportunity to discuss how my background matches your needs. "
            "Thank you for your time and consideration.\n\n"
            "Sincerely,\n"
            "Your Name\n"
        )

    prompt = f"""
Write a short professional cover letter.

Resume:
{resume_text}

Job Title: {job['title']}
Company: {job['company']}

Job Description:
{job['description']}

Keep it concise and tailored.
"""

    try:
        return _call_gemini_with_retry(prompt)
    except Exception as e:
        # Fallback to template cover letter if Gemini API calls fail permanently
        if _is_quota_error(e):
            return _fallback_letter()
        raise