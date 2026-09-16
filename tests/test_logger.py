from logger import append_turn, init_log, new_log_path


def test_new_log_path_incluye_slot_y_modelo(tmp_path):
    path = new_log_path("1", "openai/gpt-5.6-luna", base_dir=str(tmp_path))
    assert path.endswith(".md")
    assert "slot1" in path
    assert "openai_gpt-5.6-luna" in path


def test_init_log_crea_encabezado(tmp_path):
    path = new_log_path("2", "anthropic/claude-haiku-4.5", base_dir=str(tmp_path))
    init_log(path, "2", "anthropic/claude-haiku-4.5")
    texto = open(path, encoding="utf-8").read()
    assert "slot 2" in texto
    assert "anthropic/claude-haiku-4.5" in texto


def test_append_turn_registra_rol_mensaje_y_usage(tmp_path):
    path = new_log_path("4", "deepseek/deepseek-v4-flash-0731", base_dir=str(tmp_path))
    init_log(path, "4", "deepseek/deepseek-v4-flash-0731")
    append_turn(path, "user", "hola, como estas?")
    append_turn(
        path,
        "assistant",
        "todo bien, vos?",
        usage={"prompt_tokens": 12, "completion_tokens": 6},
    )
    texto = open(path, encoding="utf-8").read()
    assert "## user" in texto
    assert "hola, como estas?" in texto
    assert "## assistant" in texto
    assert "todo bien, vos?" in texto
    assert "[usage] prompt=12 completion=6" in texto
