"""
LLM fallback path, as described in Chapter Five, Section 5.4:
used when intent classification confidence falls below the 0.70 threshold.
Requires OPENAI_API_KEY to be set; degrades gracefully to a safe
escalation message if no key is configured (e.g. in a local demo).
"""
import os

SYSTEM_PROMPT = (
    "You are a customer support assistant for a small organisation. "
    "Answer only questions related to billing, technical troubleshooting, "
    "account management, or general enquiries about the service. "
    "If the question is outside this domain, politely say you are unable "
    "to help with that and suggest speaking to a human agent. "
    "Keep responses concise (2-4 sentences)."
)


def generate_fallback_response(query_text: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return (
            "I'm not fully confident I can answer that accurately. "
            "I'm connecting you with a human support agent who can help further."
        )

    try:
        import openai
        openai.api_key = api_key
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query_text},
            ],
            max_tokens=200,
            temperature=0.4,
        )
        return completion["choices"][0]["message"]["content"].strip()
    except Exception:
        return (
            "I'm having trouble generating a response right now. "
            "I'm connecting you with a human support agent who can help further."
        )
