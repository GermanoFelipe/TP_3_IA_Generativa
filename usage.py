"""Formateo del campo `usage` que devuelve OpenRouter en cada respuesta."""


def format_usage(usage: dict) -> str:
    prompt = usage.get("prompt_tokens", 0)
    completion = usage.get("completion_tokens", 0)
    reasoning = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens", 0) or 0
    cached = (usage.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0
    cost = usage.get("cost")
    cost_str = f"${cost:.6f}" if isinstance(cost, (int, float)) else "N/D"
    return (
        f"[usage] prompt={prompt} completion={completion} "
        f"reasoning={reasoning} cached={cached} cost={cost_str}"
    )


def hubo_cache_hit(usage: dict) -> bool:
    cached = (usage.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0
    return cached > 0
