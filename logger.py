"""Guarda el log de cada conversacion en un archivo .md (rol, mensaje, usage)."""

import os
from datetime import datetime

from usage import format_usage

DEFAULT_LOG_DIR = "logs"


def new_log_path(slot_key: str, model_id: str, base_dir: str = DEFAULT_LOG_DIR) -> str:
    os.makedirs(base_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    safe_model = model_id.replace("/", "_")
    return os.path.join(base_dir, f"slot{slot_key}_{safe_model}_{ts}.md")


def init_log(path: str, slot_key: str, model_id: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Conversacion - slot {slot_key} - {model_id}\n\n")
        f.write(f"Iniciada: {datetime.now().isoformat()}\n\n")


def append_turn(path: str, role: str, content: str, usage: dict | None = None) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"## {role}\n\n{content}\n\n")
        if usage is not None:
            f.write(f"{format_usage(usage)}\n\n")
