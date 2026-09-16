from usage import format_usage


def test_format_usage_con_todos_los_campos():
    usage = {
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "prompt_tokens_details": {"cached_tokens": 20},
        "completion_tokens_details": {"reasoning_tokens": 10},
        "cost": 0.001234,
    }
    linea = format_usage(usage)
    assert "prompt=100" in linea
    assert "completion=50" in linea
    assert "reasoning=10" in linea
    assert "cached=20" in linea
    assert "$0.001234" in linea


def test_format_usage_sin_campos_opcionales():
    linea = format_usage({"prompt_tokens": 5, "completion_tokens": 2})
    assert "prompt=5" in linea
    assert "completion=2" in linea
    assert "reasoning=0" in linea
    assert "cached=0" in linea


def test_format_usage_vacio_no_rompe():
    linea = format_usage({})
    assert "prompt=0" in linea
    assert "N/D" in linea


def test_hubo_cache_hit():
    from usage import hubo_cache_hit

    assert hubo_cache_hit({"prompt_tokens_details": {"cached_tokens": 500}}) is True
    assert hubo_cache_hit({"prompt_tokens_details": {"cached_tokens": 0}}) is False
    assert hubo_cache_hit({}) is False
