import json

import pytest

FLASH = {
    "components": ["nitrogen", "methane"],
    "z": [0.4, 0.6],
    "T_unit": "K",
    "P_unit": "bar",
    "T": 150,
    "P": 20,
    "eos_model": "PR",
}


def get(client, data):
    response = client.generic("GET", "/get/", json.dumps(data), content_type="application/json")
    assert response.status_code == 200
    return response.json()


def test_flash_two_phase(client):
    result = get(client, FLASH)
    assert result["V"] == pytest.approx(0.8038, abs=1e-3)
    assert result["x"] == pytest.approx([0.1612, 0.8388], abs=1e-3)
    assert result["y"] == pytest.approx([0.4583, 0.5417], abs=1e-3)
    assert result["P_bubl"] == pytest.approx(33.46, abs=0.05)
    assert result["P_dew"] == pytest.approx(17.92, abs=0.05)


@pytest.mark.parametrize(("unit", "value"), [("atm", 20 / 1.01325), ("kpa", 2000), ("psi", 20 / 0.068948)])
def test_pressure_units_agree(client, unit, value):
    result = get(client, {**FLASH, "P_unit": unit, "P": value})
    assert result["V"] == pytest.approx(0.8038, abs=1e-3)


@pytest.mark.parametrize(("unit", "value"), [("C", 150 - 273.15), ("F", (150 - 273.15) * 9 / 5 + 32)])
def test_temperature_units_agree(client, unit, value):
    result = get(client, {**FLASH, "T_unit": unit, "T": value})
    assert result["V"] == pytest.approx(0.8038, abs=1e-3)


def test_srk_reports_subcooled(client):
    result = get(client, {**FLASH, "eos_model": "SRK"})
    assert result["V"] is None
    assert "SUB-COOLED" in result["message_initiate"]


def test_missing_key_is_reported(client):
    data = {k: v for k, v in FLASH.items() if k != "eos_model"}
    assert "can not be procced" in get(client, data)["Message"]
