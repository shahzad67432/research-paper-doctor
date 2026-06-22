import json
import os
import re
import sys
import time

import requests
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_MODEL = "gemini-1.5-flash"
OPENROUTER_MODEL = "qwen/qwen3-coder:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def any_key_available() -> bool:
    return bool(GEMINI_API_KEY) or bool(OPENROUTER_API_KEY)

RETRY_DELAYS = [5, 15, 30]


def _call_openrouter(system_prompt: str, user_prompt: str, model: str) -> str:
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set in .env")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 2000,
        "temperature": 0.3,
    }

    resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    choices = data.get("choices", [])
    if not choices:
        raise ValueError("OpenRouter returned no choices")
    content = choices[0].get("message", {}).get("content", "")
    return content.strip()


def call_gemini(
    system_prompt: str,
    user_prompt: str,
    model: str = GEMINI_MODEL,
) -> str:
    last_error = None

    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)

        for attempt, delay in enumerate(RETRY_DELAYS):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=user_prompt,
                    config={
                        "system_instruction": system_prompt,
                        "max_output_tokens": 2000,
                        "temperature": 0.3,
                    },
                )
                return response.text.strip()
            except Exception as e:
                error_str = str(e)
                is_quota = "429" in error_str or "RESOURCE_EXHAUSTED" in error_str
                if is_quota and attempt < len(RETRY_DELAYS) - 1:
                    print(
                        f"Gemini rate limited, retrying in {delay}s...",
                        file=sys.stderr,
                    )
                    time.sleep(delay)
                    continue
                last_error = e
                if not is_quota:
                    break

    if OPENROUTER_API_KEY:
        print("Gemini quota exhausted, falling back to OpenRouter...", file=sys.stderr)
        try:
            return _call_openrouter(system_prompt, user_prompt, OPENROUTER_MODEL)
        except Exception as e:
            last_error = e
            raise

    if last_error:
        raise last_error
    raise ValueError("No LLM provider available — set GEMINI_API_KEY or OPENROUTER_API_KEY in .env")


def parse_json_response(text: str) -> dict | list:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = re.sub(r"<pad>\s*", "", cleaned)
    cleaned = cleaned.strip()
    try:
        result = json.loads(cleaned)
        if isinstance(result, (dict, list)):
            return result
        raise ValueError(f"JSON result is not a dict or list: {type(result)}")
    except json.JSONDecodeError:
        preview = text[:200]
        raise ValueError(
            f"Failed to parse LLM JSON response (first 200 chars):\n{preview}"
        )
