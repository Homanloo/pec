import json

import numpy as np
import pytest
from django.test import Client, override_settings

from pec import equilibrium as eq
from pec.components import get_component
from pec.saturation import saturation_pressure

client = Client()
GAS = {
    "eos": "PR",
    "components": ["Methane", "Ethane", "n-Propane", "n-Butane", "n-Pentane"],
    "z": [0.4, 0.2, 0.15, 0.15, 0.1],
}
CORE = [get_component(n) for n in GAS["components"]]


def post(url, body):
    return client.post(url, json.dumps(body), content_type="application/json")


def test_components_models_and_health():
    assert len(client.get("/api/v1/components/").json()) == 102
    assert client.get("/api/v1/components/Water/").json()["Tc"] == get_component("Water").Tc
    assert client.get("/api/v1/components/water/").status_code == 404
    assert [m["name"] for m in client.get("/api/v1/models/").json()] == ["vdW", "RK", "SRK", "PR"]
    assert client.get("/api/v1/health/").json()["status"] == "ok"


def test_flash_is_the_core_flash_with_units_and_normalisation():
    # 26.85 °C and 30 bar are 300 K and 3 MPa; z given unnormalised (sum 2)
    body = {**GAS, "z": [0.8, 0.4, 0.3, 0.3, 0.2], "T": {"value": 26.85, "unit": "degC"}}
    r = post("/api/v1/flash/", {**body, "P": {"value": 30, "unit": "bar"}}).json()
    V, x, y = eq.flash("PR", CORE, 300.0, 3e6, np.array(GAS["z"]))
    liquid, vapour = r["phases"]
    assert (liquid["name"], vapour["name"]) == ("liquid", "vapour")
    assert vapour["fraction"] == pytest.approx(V, rel=1e-12)
    assert liquid["composition"] == pytest.approx(x, rel=1e-12)
    assert vapour["composition"] == pytest.approx(y, rel=1e-12)
    # One phase: labelled, no K
    r = post("/api/v1/flash/", {**GAS, "T": 350, "P": 1e6}).json()
    assert [p["name"] for p in r["phases"]] == ["vapour"]
    assert r["K"] is None


def test_saturation_point_and_calculation_errors():
    r = post("/api/v1/saturation-point/", {**GAS, "kind": "bubble", "T": 300}).json()
    P, y = eq.bubble_pressure("PR", CORE, 300.0, np.array(GAS["z"]))
    assert r["P"] == pytest.approx(P, rel=1e-12)
    assert r["incipient"]["composition"] == pytest.approx(y, rel=1e-12)
    # No dew point above the cricondentherm: 422 with the core's message
    r = post("/api/v1/saturation-point/", {**GAS, "kind": "dew", "T": 450})
    assert r.status_code == 422
    assert "dew point not found" in r.json()["detail"]


def test_invalid_input_is_400_with_a_message_per_field():
    bad = [
        ({**GAS, "components": ["Methane", "Nope"], "z": [0.5, 0.5]}, "components"),
        ({**GAS, "z": [0.5, 0.5]}, "z"),
        ({**GAS, "z": [0.4, 0.2, 0.15, 0.15, 0.0]}, "z"),
        ({**GAS, "T": {"value": 300, "unit": "kelvin"}}, "T"),
        ({**GAS, "T": -5}, "T"),
        ({**GAS, "kij": [[0, 0.1], [0.1, 0]]}, "kij"),
        ({**GAS, "eos": "GERG"}, "eos"),
    ]
    for body, field in bad:
        r = post("/api/v1/flash/", {"T": 300, "P": 1e6, **body})
        assert r.status_code == 400, field
        assert field in r.json(), field
    r = post("/api/v1/saturation-point/", {**GAS, "kind": "dew", "T": 300, "P": 1e6})
    assert r.status_code == 400  # T and P both given


def test_sweeps():
    # P-x-y: the ends are the pure components' vapour pressures
    body = {"eos": "PR", "components": ["Ethane", "n-Propane"], "kind": "Pxy", "T": 250}
    r = post("/api/v1/binary/", {**body, "points": 11}).json()
    assert len(r["points"]) == 11
    assert r["failed"] == []
    ends = r["points"][0]["P"], r["points"][-1]["P"]
    pure = [saturation_pressure("PR", get_component(n), 250.0) for n in ("n-Propane", "Ethane")]
    assert ends == pytest.approx(pure, rel=1e-12)
    # Methane is supercritical at 300 K: points it cannot reach are reported, not dropped
    body = {"eos": "PR", "components": ["Methane", "n-Butane"], "kind": "Pxy", "T": 300}
    r = post("/api/v1/binary/", {**body, "points": 11}).json()
    assert 1.0 in r["failed"]
    assert len(r["points"]) + len(r["failed"]) == 11
    # Envelope, pure curve and isotherms
    r = post("/api/v1/envelope/", {**GAS, "points": 20}).json()
    assert len(r["bubble"]) > 10
    assert len(r["dew"]) > 10
    r = post("/api/v1/pure/curve/", {"component": "Water", "points": 10}).json()
    assert all(p["V_liquid"] < r["Vc"] < p["V_vapour"] for p in r["points"])
    r = post("/api/v1/pure/isotherms/", {"component": "Methane", "temperatures": [150, 250]})
    assert [("saturation" in i) for i in r.json()["isotherms"]] == [True, False]


def test_docs_and_frontend(tmp_path):
    assert client.get("/api/schema/").status_code == 200
    assert client.get("/api/docs/").status_code == 200
    (tmp_path / "index.html").write_text("<!doctype html><title>PEC</title>")
    with override_settings(FRONTEND_DIST=tmp_path):
        r = client.get("/flash")  # any page path gets the app
        assert r.status_code == 200
        assert b"<title>PEC</title>" in b"".join(r.streaming_content)
