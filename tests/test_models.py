import pytest

from models import SLOTS, get_slot


def test_hay_cuatro_slots():
    assert len(SLOTS) == 4


def test_cada_slot_es_de_un_proveedor_distinto():
    proveedores = {slot.model_id.split("/")[0] for slot in SLOTS}
    assert len(proveedores) == 4


def test_get_slot_valido():
    slot = get_slot("2")
    assert slot.model_id == "anthropic/claude-haiku-4.5"
    assert slot.supports_cache is True


def test_get_slot_invalido():
    with pytest.raises(KeyError):
        get_slot("9")


def test_solo_slot_1_soporta_effort():
    assert [s.key for s in SLOTS if s.supports_effort] == ["1"]


def test_solo_slot_3_soporta_structured_output():
    assert [s.key for s in SLOTS if s.supports_structured_output] == ["3"]
