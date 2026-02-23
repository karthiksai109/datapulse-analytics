import os
import logging

logger = logging.getLogger("datapulse-flask-ai")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


def get_openai_client():
    if not OPENAI_API_KEY:
        logger.warning("OpenAI API key not configured")
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        return client
    except Exception as e:
        logger.warning(f"OpenAI client unavailable: {e}")
        return None


def generate_openai_insights(content: str, max_tokens: int = 500) -> dict:
    client = get_openai_client()

    if not client:
        return _fallback_insights(content)

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior data analyst. Provide clear, actionable insights from analytics data.",
                },
                {"role": "user", "content": content},
            ],
            max_tokens=max_tokens,
            temperature=0.3,
        )

        text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens

        logger.info(f"OpenAI insights generated, tokens={tokens_used}")
        return {"text": text, "tokens_used": tokens_used, "provider": "openai"}

    except Exception as e:
        logger.error(f"OpenAI call failed: {e}")
        return _fallback_insights(content)


def generate_code_suggestion(prompt: str) -> dict:
    client = get_openai_client()
    if not client:
        return {"code": "", "explanation": "OpenAI unavailable", "provider": "fallback"}

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a Python expert. Generate clean, efficient code for data analytics tasks.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
            temperature=0.2,
        )

        text = response.choices[0].message.content
        return {"code": text, "tokens_used": response.usage.total_tokens, "provider": "openai"}

    except Exception as e:
        logger.error(f"OpenAI code suggestion failed: {e}")
        return {"code": "", "explanation": str(e), "provider": "fallback"}


def _fallback_insights(content: str) -> dict:
    words = content.split()
    return {
        "text": (
            f"Data analysis processed ({len(words)} words). "
            f"[Configure OPENAI_API_KEY for full AI-powered insights]"
        ),
        "tokens_used": 0,
        "provider": "fallback",
    }
