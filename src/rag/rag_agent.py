import os
from rag.vector_store import search
from agent_utils.retry_helper import retry_with_backoff

_client = None

def _get_client():
    """Lazily initialize the GenAI Client to prevent issues on module load."""
    global _client
    if _client is None:
        print("[GEMINI-RAG] Initializing Gemini API client lazily...")
        from google import genai
        _client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )
        print("[GEMINI-RAG] Gemini API client initialized successfully.")
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

def career_advice(question):
    """
    Retrieves relevant career documentation chunks and uses Gemini to generate career advice.
    Robustly handles rate limits and service unavailability.
    """
    try:
        docs = search(question)
        context = "\n".join(docs)
    except Exception as e:
        # If vector search fails (e.g., missing index files), log and provide generic context
        context = "No career documents available."

    prompt = f"""
You are a career advisor.

Use the following knowledge to answer the question.

Knowledge:
{context}

Question:
{question}

Provide clear career advice.
"""

    try:
        return _call_gemini_with_retry(prompt)
    except Exception as e:
        # Fallback to pure RAG context if Gemini API calls fail permanently
        if _is_quota_error(e):
            return (
                "Gemini is experiencing high demand or rate limits; here is the most relevant matching knowledge:\n\n"
                + context
            )
        raise