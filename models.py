"""Configuracion de los 4 slots de modelos servidos via OpenRouter."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSlot:
    key: str
    model_id: str
    label: str
    capability: str
    supports_effort: bool = False
    supports_cache: bool = False
    supports_structured_output: bool = False


SLOTS = [
    ModelSlot(
        key="1",
        model_id="openai/gpt-5.6-luna",
        label="GPT-5.6 Luna (OpenAI)",
        capability="Effort configurable",
        supports_effort=True,
    ),
    ModelSlot(
        key="2",
        model_id="anthropic/claude-haiku-4.5",
        label="Claude Haiku 4.5 (Anthropic)",
        capability="Prompt caching explicito",
        supports_cache=True,
    ),
    ModelSlot(
        key="3",
        model_id="google/gemini-3.7-flash",
        label="Gemini 3.7 Flash (Google)",
        capability="Salidas estructuradas (JSON Schema)",
        supports_structured_output=True,
    ),
    ModelSlot(
        key="4",
        model_id="deepseek/deepseek-v4-flash-0731",
        label="DeepSeek V4 Flash (DeepSeek)",
        capability="El escalon barato",
    ),
]


def get_slot(key: str) -> ModelSlot:
    for slot in SLOTS:
        if slot.key == key:
            return slot
    raise KeyError(key)
