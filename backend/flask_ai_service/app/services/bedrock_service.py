import os
import json
import logging

logger = logging.getLogger("datapulse-flask-ai")

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-v2")


def get_bedrock_client():
    try:
        import boto3
        client = boto3.client(
            "bedrock-runtime",
            region_name=AWS_REGION,
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", ""),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
        )
        return client
    except Exception as e:
        logger.warning(f"Bedrock client unavailable: {e}")
        return None


def generate_bedrock_summary(content: str, max_tokens: int = 500) -> dict:
    client = get_bedrock_client()

    if not client:
        logger.info("Bedrock unavailable, using fallback summary")
        return _fallback_summary(content)

    try:
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": f"You are a data analytics expert. Analyze and summarize the following:\n\n{content}",
                }
            ],
            "temperature": 0.3,
            "top_p": 0.9,
        })

        response = client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=body,
            contentType="application/json",
            accept="application/json",
        )

        response_body = json.loads(response["body"].read())
        text = response_body["content"][0]["text"]
        tokens_used = response_body.get("usage", {}).get("output_tokens", 0)

        logger.info(f"Bedrock summary generated, tokens={tokens_used}")
        return {"text": text, "tokens_used": tokens_used, "provider": "bedrock"}

    except Exception as e:
        logger.error(f"Bedrock invocation failed: {e}")
        return _fallback_summary(content)


def _fallback_summary(content: str) -> dict:
    words = content.split()
    word_count = len(words)
    preview = " ".join(words[:50]) + ("..." if word_count > 50 else "")

    return {
        "text": (
            f"Analysis of provided data ({word_count} words processed). "
            f"Key content: {preview} "
            f"[AI summary generated in fallback mode - configure AWS Bedrock credentials for full AI analysis]"
        ),
        "tokens_used": 0,
        "provider": "fallback",
    }
