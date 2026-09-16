"""Cliente minimo para la API de OpenRouter (formato compatible con OpenAI)."""

import os

import requests

API_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterError(RuntimeError):
    pass


def _headers() -> dict:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise OpenRouterError("Falta OPENROUTER_API_KEY (revisa tu .env).")
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def send_chat(
    model: str,
    messages: list,
    reasoning: dict | None = None,
    response_format: dict | None = None,
) -> tuple[str, dict]:
    payload = {"model": model, "messages": messages}
    if reasoning:
        payload["reasoning"] = reasoning
    if response_format:
        payload["response_format"] = response_format

    resp = requests.post(API_URL, headers=_headers(), json=payload, timeout=120)
    if resp.status_code != 200:
        raise OpenRouterError(f"OpenRouter error {resp.status_code}: {resp.text}")

    data = resp.json()
    choice = data["choices"][0]
    content = choice["message"]["content"]
    usage = data.get("usage", {})
    return content, usage
