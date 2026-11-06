"""API v1: thin views over `pec`. Inputs are checked and converted to SI by serializers.py;
outputs are SI (K, Pa, m³/mol). Status codes: 400 invalid input, 404 unknown component,
422 the calculation has no answer (e.g. no dew point at that T) or did not converge."""

import dataclasses
import time
from importlib.metadata import version

import numpy as np
from django.conf import settings
from django.http import FileResponse, Http404
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from pec import equilibrium as eq
from pec.components import COMPONENTS
from pec.constants import R
from pec.eos import EOS, VC_OVER_B, ln_phi, mixture_parameters, pressure
from pec.saturation import saturation_pressure, saturation_temperature
from pecweb import serializers as s

# What `pec` raises when a calculation has no answer or does not converge
CALCULATION_ERRORS = (ValueError, RuntimeError, ArithmeticError)
TIME_BUDGET = 10.0  # s, for the sweeps (D-15)

MODELS = {
    "vdW": "van der Waals (1873)",
    "RK": "Redlich–Kwong (1949)",
    "SRK": "Soave–Redlich–Kwong (1972)",
    "PR": "Peng–Robinson (1976)",
}
ERRORS = {
    400: OpenApiResponse(description="Invalid input (message per field)"),
    422: OpenApiResponse(description="No solution or no convergence; `detail` says why"),
}
NATURAL_GAS = {
    "eos": "PR",
    "components": ["Methane", "Ethane", "n-Propane", "n-Butane", "n-Pentane"],
    "z": [0.4, 0.2, 0.15, 0.15, 0.1],
}


def validated(serializer, request):
    ser = serializer(data=request.data)
    ser.is_valid(raise_exception=True)
    return ser.validated_data


def unprocessable(error):
    return Response({"detail": str(error)}, status=422)


def check_time(start):
    if time.monotonic() - start > TIME_BUDGET:
        raise RuntimeError(f"time budget of {TIME_BUDGET:.0f} s exceeded; ask for fewer points")


def phase(d, T, P, x, name, fraction, root="stable"):
    """One phase of a result: composition, Z and molar volume."""
    Z, _ = ln_phi(d["eos"], d["components"], T, P, x, root, d["kij"])
    return {
        "name": name,
        "fraction": fraction,
        "composition": [float(v) for v in x],
        "Z": Z,
        "V": Z * R * T / P,
    }


@extend_schema(responses={200: OpenApiResponse(description="Service is up")})
@api_view(["GET"])
def health(request):
    return Response({"status": "ok", "version": version("pec")})


@extend_schema(responses={200: OpenApiResponse(description="The available equations of state")})
@api_view(["GET"])
def models(request):
    return Response([{"name": name, "title": MODELS[name]} for name in EOS])


@extend_schema(responses={200: OpenApiResponse(description="All components (SI units)")})
@api_view(["GET"])
def components(request):
    return Response([dataclasses.asdict(c) for c in COMPONENTS.values()])


@extend_schema(responses={200: OpenApiResponse(description="One component"), 404: None})
@api_view(["GET"])
def component(request, name):
    if name not in COMPONENTS:
        raise NotFound(f"unknown component {name!r}")
    return Response(dataclasses.asdict(COMPONENTS[name]))


@extend_schema(
    request=s.Flash,
    responses={200: OpenApiResponse(description="One or two phases"), **ERRORS},
    examples=[
        OpenApiExample("Two phases", value={**NATURAL_GAS, "T": 300, "P": 3e6}),
        OpenApiExample(
            "With units",
            value={
                **NATURAL_GAS,
                "T": {"value": 26.85, "unit": "degC"},
                "P": {"value": 30, "unit": "bar"},
            },
        ),
    ],
)
@api_view(["POST"])
def flash(request):
    """Isothermal flash: stability test, then the phase split (Michelsen, 1982)."""
    d = validated(s.Flash, request)
    T, P, z = d["T"], d["P"], d["z"]
    try:
        result = eq.flash(d["eos"], d["components"], T, P, z, d["kij"])
        if result is None:
            label = eq.phase_label(d["eos"], d["components"], T, P, z, d["kij"])
            return Response({"T": T, "P": P, "phases": [phase(d, T, P, z, label, 1.0)], "K": None})
        V, x, y = result
        phases = [phase(d, T, P, x, "liquid", 1 - V), phase(d, T, P, y, "vapour", V)]
        return Response({"T": T, "P": P, "phases": phases, "K": [float(v) for v in y / x]})
    except CALCULATION_ERRORS as e:
        return unprocessable(e)


@extend_schema(
    request=s.SaturationPoint,
    responses={200: OpenApiResponse(description="T, P and the incipient phase"), **ERRORS},
    examples=[
        OpenApiExample(
            "Bubble pressure at 300 K", value={**NATURAL_GAS, "kind": "bubble", "T": 300}
        ),
        OpenApiExample("Dew temperature at 30 bar", value={**NATURAL_GAS, "kind": "dew", "P": 3e6}),
    ],
)
@api_view(["POST"])
def saturation_point(request):
    """Bubble or dew point: give T to find P, or P to find T."""
    d = validated(s.SaturationPoint, request)
    bubble = d["kind"] == "bubble"
    args = (d["eos"], d["components"])
    try:
        if "T" in d:
            T = d["T"]
            P, w = (eq.bubble_pressure if bubble else eq.dew_pressure)(*args, T, d["z"], d["kij"])
        else:
            P = d["P"]
            T, w = (eq.bubble_temperature if bubble else eq.dew_temperature)(
                *args, P, d["z"], d["kij"]
            )
        feed = "liquid" if bubble else "vapour"
        incipient = "vapour" if bubble else "liquid"
        x, y = (d["z"], w) if bubble else (w, d["z"])
        return Response(
            {
                "kind": d["kind"],
                "T": T,
                "P": P,
                "feed": phase(d, T, P, d["z"], feed, 1.0, feed),
                "incipient": phase(d, T, P, w, incipient, 0.0, incipient),
                "K": [float(v) for v in y / x],
            }
        )
    except CALCULATION_ERRORS as e:
        return unprocessable(e)


@extend_schema(
    request=s.Envelope,
    responses={200: OpenApiResponse(description="Bubble and dew curves, (T, P) points"), **ERRORS},
    examples=[OpenApiExample("Natural gas", value={**NATURAL_GAS, "points": 40})],
)
@api_view(["POST"])
def envelope(request):
    """P-T phase envelope, v1: bubble and dew temperatures over a pressure sweep from 10 kPa up
    to where each curve ends (near the critical point and cricondenbar the sweep stops; Phase 4
    replaces it with continuation through the critical point)."""
    d = validated(s.Envelope, request)
    start = time.monotonic()
    pressures = np.geomspace(1e4, 3 * max(c.Pc for c in d["components"]), d["points"])
    curves = {}
    try:
        for kind, solve in (("bubble", eq.bubble_temperature), ("dew", eq.dew_temperature)):
            curve = []
            for P in pressures:
                check_time(start)
                try:
                    T, _ = solve(d["eos"], d["components"], P, d["z"], d["kij"])
                except CALCULATION_ERRORS:
                    if curve:
                        break  # the curve has ended (critical region)
                    continue
                curve.append({"T": T, "P": float(P)})
            curves[kind] = curve
    except CALCULATION_ERRORS as e:
        return unprocessable(e)
    return Response(curves)


@extend_schema(
    request=s.Binary,
    responses={200: OpenApiResponse(description="Bubble (x) and dew (y) curves"), **ERRORS},
    examples=[
        OpenApiExample(
            "P-x-y of ethane/propane at 250 K",
            value={"eos": "PR", "components": ["Ethane", "n-Propane"], "kind": "Pxy", "T": 250},
        ),
        OpenApiExample(
            "T-x-y of benzene/toluene at 1 atm",
            value={"eos": "PR", "components": ["Benzene", "Toluene"], "kind": "Txy", "P": 101325},
        ),
    ],
)
@api_view(["POST"])
def binary(request):
    """Binary P-x-y (fixed T) or T-x-y (fixed P): a bubble point at each x₁ from 0 to 1 gives
    both curves, P or T against x₁ and against the vapour y₁. The ends are the pure
    components' saturation points. Points that fail (e.g. beyond a mixture critical point) are
    listed in `failed` instead of being dropped silently (legacy bug B-13)."""
    d = validated(s.Binary, request)
    eos, (c1, c2), kij = d["eos"], d["components"], d["kij"]
    Pxy = d["kind"] == "Pxy"
    start = time.monotonic()
    points, failed = [], []
    try:
        for x1 in np.linspace(0, 1, d["points"]):
            x1 = float(x1)
            check_time(start)
            try:
                if x1 in (0.0, 1.0):  # pure component
                    c = c1 if x1 == 1.0 else c2
                    if Pxy:
                        T, P = d["T"], saturation_pressure(eos, c, d["T"])
                    else:
                        T, P = saturation_temperature(eos, c, d["P"]), d["P"]
                    y1 = x1
                elif Pxy:
                    T = d["T"]
                    P, y = eq.bubble_pressure(eos, [c1, c2], T, [x1, 1 - x1], kij)
                    y1 = float(y[0])
                else:
                    P = d["P"]
                    T, y = eq.bubble_temperature(eos, [c1, c2], P, [x1, 1 - x1], kij)
                    y1 = float(y[0])
            except CALCULATION_ERRORS:
                failed.append(x1)
                continue
            points.append({"x": x1, "y": y1, "T": T, "P": P})
    except CALCULATION_ERRORS as e:
        return unprocessable(e)
    return Response({"kind": d["kind"], "points": points, "failed": failed})


@extend_schema(
    request=s.PureCurve,
    responses={200: OpenApiResponse(description="P^sat and saturated volumes up to Tc"), **ERRORS},
    examples=[OpenApiExample("Water", value={"eos": "PR", "component": "Water", "points": 60})],
)
@api_view(["POST"])
def pure_curve(request):
    """Vapour-pressure curve of a pure component from 0.45 Tc to 0.9999 Tc, with the saturated
    liquid and vapour molar volumes (the P-V dome)."""
    d = validated(s.PureCurve, request)
    eos, c = d["eos"], d["component"]
    b = mixture_parameters(eos, [c], c.Tc, [1.0])[1]
    points = []
    try:
        for T in c.Tc * np.linspace(0.45, 0.9999, d["points"]):
            T = float(T)
            P = saturation_pressure(eos, c, T)
            ZL, _ = ln_phi(eos, [c], T, P, [1.0], "liquid")
            ZV, _ = ln_phi(eos, [c], T, P, [1.0], "vapour")
            points.append({"T": T, "P": P, "V_liquid": ZL * R * T / P, "V_vapour": ZV * R * T / P})
    except CALCULATION_ERRORS as e:
        return unprocessable(e)
    return Response({"Tc": c.Tc, "Pc": c.Pc, "Vc": VC_OVER_B[eos] * b, "points": points})


@extend_schema(
    request=s.Isotherms,
    responses={200: OpenApiResponse(description="P(V) per temperature"), **ERRORS},
    examples=[
        OpenApiExample(
            "Methane",
            value={"eos": "PR", "component": "Methane", "temperatures": [150, 170, 190.564, 210]},
        )
    ],
)
@api_view(["POST"])
def isotherms(request):
    """P-V isotherms of a pure component, P(V) from the EOS itself on V from 1.1 b to 30 Vc,
    with the saturation point (P^sat and both volumes) for each T below Tc."""
    d = validated(s.Isotherms, request)
    eos, c = d["eos"], d["component"]
    b = mixture_parameters(eos, [c], c.Tc, [1.0])[1]
    V = np.geomspace(1.1 * b, 30 * VC_OVER_B[eos] * b, d["points"])
    result = []
    try:
        for T in d["temperatures"]:
            item = {"T": T, "V": V.tolist(), "P": pressure(eos, [c], T, V, [1.0]).tolist()}
            if T < c.Tc:
                P = saturation_pressure(eos, c, T)
                ZL, _ = ln_phi(eos, [c], T, P, [1.0], "liquid")
                ZV, _ = ln_phi(eos, [c], T, P, [1.0], "vapour")
                item["saturation"] = {
                    "P": P,
                    "V_liquid": ZL * R * T / P,
                    "V_vapour": ZV * R * T / P,
                }
            result.append(item)
    except CALCULATION_ERRORS as e:
        return unprocessable(e)
    return Response({"Tc": c.Tc, "Pc": c.Pc, "Vc": VC_OVER_B[eos] * b, "isotherms": result})


def spa(request):
    """The frontend's index.html for every non-API path; the app routes in the browser."""
    index = settings.FRONTEND_DIST / "index.html"
    if not index.is_file():
        raise Http404("frontend not built: run `just build`")
    response = FileResponse(index.open("rb"), content_type="text/html")
    response["Cache-Control"] = "no-cache"  # assets are hashed; the page itself must be fresh
    return response
