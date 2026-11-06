"""Request validation. Everything is converted to SI and checked here, so the views only call
`pec` with clean inputs. Limits (D-15): at most 10 components and 200 points per request."""

import numpy as np
from rest_framework import serializers

from pec import units
from pec.components import COMPONENTS
from pec.eos import EOS

MAX_COMPONENTS = 10
MAX_POINTS = 200


class Quantity(serializers.Field):
    """A temperature or pressure: a plain number in SI (K, Pa) or {"value": 25, "unit": "degC"}.
    Converted to SI; must be positive (absolute T and P)."""

    def __init__(self, kind, **kwargs):
        self.kind = kind  # "T" or "P"
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        table, convert = (
            (units.TEMPERATURE_UNITS, units.to_kelvin)
            if self.kind == "T"
            else (units.PRESSURE_UNITS, units.to_pascal)
        )
        if isinstance(data, dict):
            value, unit = data.get("value"), data.get("unit")
            if unit not in table:
                raise serializers.ValidationError(f"unit must be one of {sorted(table)}")
        else:
            value, unit = data, "K" if self.kind == "T" else "Pa"
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise serializers.ValidationError("must be a number or {value, unit}")
        si = convert(float(value), unit)
        if not si > 0:
            raise serializers.ValidationError("must be above absolute zero")
        return si

    def to_representation(self, value):
        return value


def component_names(value):
    unknown = [n for n in value if n not in COMPONENTS]
    if unknown:
        raise serializers.ValidationError(
            f"unknown component(s): {unknown}; see /api/v1/components/"
        )
    if len(set(value)) != len(value):
        raise serializers.ValidationError("components must not repeat")
    return value


class Base(serializers.Serializer):
    eos = serializers.ChoiceField(choices=list(EOS), default="PR")


def names_field(min_length=1, max_length=MAX_COMPONENTS):
    return serializers.ListField(
        child=serializers.CharField(),
        min_length=min_length,
        max_length=max_length,
        validators=[component_names],
        help_text="Component names, see /api/v1/components/",
    )


def kij_field():
    return serializers.ListField(
        child=serializers.ListField(child=serializers.FloatField()),
        required=False,
        help_text="Symmetric n×n binary interaction parameters, zero diagonal (default zeros)",
    )


def clean_kij(kij, n):
    """The k_ij matrix as an array (None if not given), after checking its shape."""
    if kij is None:
        return None
    kij = np.array(kij, dtype=float)
    if kij.shape != (n, n) or not np.allclose(kij, kij.T) or np.any(np.diag(kij) != 0):
        raise serializers.ValidationError(
            {"kij": f"must be a symmetric {n}×{n} matrix with a zero diagonal"}
        )
    return kij


class Mixture(Base):
    components = names_field()
    z = serializers.ListField(
        child=serializers.FloatField(), help_text="Mole fractions (normalised to sum 1)"
    )
    kij = kij_field()

    def validate(self, attrs):
        n = len(attrs["components"])
        z = np.array(attrs["z"])
        if len(z) != n:
            raise serializers.ValidationError({"z": f"needs {n} values, one per component"})
        if not np.all(z > 0):
            raise serializers.ValidationError({"z": "every mole fraction must be positive"})
        attrs["z"] = z / z.sum()
        attrs["components"] = [COMPONENTS[name] for name in attrs["components"]]
        attrs["kij"] = clean_kij(attrs.get("kij"), n)
        return attrs


class Flash(Mixture):
    T = Quantity("T")
    P = Quantity("P")


class SaturationPoint(Mixture):
    kind = serializers.ChoiceField(choices=["bubble", "dew"])
    T = Quantity("T", required=False, help_text="Give T to find P, or P to find T")
    P = Quantity("P", required=False)

    def validate(self, attrs):
        if ("T" in attrs) == ("P" in attrs):
            raise serializers.ValidationError("give exactly one of T and P")
        return super().validate(attrs)


class Envelope(Mixture):
    points = serializers.IntegerField(min_value=5, max_value=MAX_POINTS, default=40)


class Binary(Base):
    components = names_field(2, 2)
    kij = kij_field()
    kind = serializers.ChoiceField(
        choices=["Pxy", "Txy"], help_text="Pxy at fixed T, Txy at fixed P"
    )
    T = Quantity("T", required=False)
    P = Quantity("P", required=False)
    points = serializers.IntegerField(min_value=3, max_value=MAX_POINTS, default=41)

    def validate(self, attrs):
        if attrs["kind"] == "Pxy" and ("T" not in attrs or "P" in attrs):
            raise serializers.ValidationError("Pxy needs T (and no P)")
        if attrs["kind"] == "Txy" and ("P" not in attrs or "T" in attrs):
            raise serializers.ValidationError("Txy needs P (and no T)")
        attrs["components"] = [COMPONENTS[name] for name in attrs["components"]]
        attrs["kij"] = clean_kij(attrs.get("kij"), 2)
        return attrs


class Pure(Base):
    component = serializers.CharField()

    def validate_component(self, value):
        return COMPONENTS[component_names([value])[0]]


class PureCurve(Pure):
    points = serializers.IntegerField(min_value=5, max_value=MAX_POINTS, default=60)


class Isotherms(Pure):
    temperatures = serializers.ListField(child=Quantity("T"), min_length=1, max_length=10)
    points = serializers.IntegerField(min_value=10, max_value=MAX_POINTS, default=150)
