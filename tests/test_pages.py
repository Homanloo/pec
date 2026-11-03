import pytest


@pytest.mark.parametrize("path", ["/", "/home/", "/vle/", "/pxy/", "/pt/", "/api/", "/docs/"])
def test_page_renders(client, path):
    assert client.get(path).status_code == 200


def test_vle_flash(client):
    response = client.post("/vle/", {
        "component_form-Components": ["nitrogen", "methane"],
        "composition_form-Composition": "0.4 0.6",
        "unit_form-T_units": "K",
        "unit_form-P_units": "bar",
        "value_form-T_value": 150,
        "value_form-P_value": 20,
        "eos_form-Eos_model": "PR",
    })
    assert response.status_code == 200
    assert response.context["V"] == pytest.approx(0.8038, abs=1e-3)


def test_vle_rejects_letters_in_composition(client):
    response = client.post("/vle/", {
        "component_form-Components": ["nitrogen", "methane"],
        "composition_form-Composition": "a b",
        "unit_form-T_units": "K",
        "unit_form-P_units": "bar",
        "value_form-T_value": 150,
        "value_form-P_value": 20,
        "eos_form-Eos_model": "PR",
    })
    assert response.context["V"] is None
    assert "right format" in response.context["Message"]


def test_pxy_draws_a_diagram(client):
    response = client.post("/pxy/", {
        "component_form-Components": ["nitrogen", "methane"],
        "temp_form-T_units": "K",
        "temp_form-T_value": 150,
        "eos_form-Eos_model": "PR",
        "node_form-Node_number": 10,
    })
    assert response.context["result_status"] == 1
    assert b"data:image/png;base64," in response.content


def test_pt_draws_a_diagram(client):
    response = client.post("/pt/", {
        "component_form-Components": ["nitrogen", "methane"],
        "eos_form-Composition": "0.4 0.6",
        "temp_form-T_units": "K",
        "temp_form-T_value_start": 80,
        "temp_form-T_value_end": 180,
        "temp_form-T_step": 10,
        "eos_form-Eos_model": "PR",
        "eos_form-Gap": 5,
    })
    assert response.context["result_status"] == 1
    assert b"data:image/png;base64," in response.content


def test_pt_converts_celsius(client):
    response = client.post("/pt/", {
        "component_form-Components": ["nitrogen", "methane"],
        "eos_form-Composition": "0.4 0.6",
        "temp_form-T_units": "C",
        "temp_form-T_value_start": 80 - 273.15,
        "temp_form-T_value_end": 180 - 273.15,
        "temp_form-T_step": 10,
        "eos_form-Eos_model": "PR",
        "eos_form-Gap": 5,
    })
    assert response.context["result_status"] == 1
