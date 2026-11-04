import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from pec import units
from pec.errors import UnitError


@pytest.mark.parametrize(
    ("value", "unit", "kelvin"),
    [
        (0.0, "K", 0.0),
        (0.0, "degC", 273.15),
        (100.0, "degC", 373.15),
        (32.0, "degF", 273.15),
        (212.0, "degF", 373.15),
        (-40.0, "degF", 233.15),  # -40 °F == -40 °C
        (491.67, "degR", 273.15),
    ],
)
def test_temperature_reference_points(value, unit, kelvin):
    assert units.to_kelvin(value, unit) == pytest.approx(kelvin, abs=1e-12)
    assert units.from_kelvin(kelvin, unit) == pytest.approx(value, abs=1e-12)


@pytest.mark.parametrize(
    ("value", "unit", "pascal"),
    [
        (1.0, "Pa", 1.0),
        (1.0, "kPa", 1e3),
        (1.0, "MPa", 1e6),
        (1.0, "bar", 1e5),
        (1.0, "atm", 101_325.0),
        (1.0, "psi", 6894.757293168361),
        (760.0, "mmHg", 101_325.0144354),  # conventional mmHg is not exactly 1/760 atm
        (760.0, "torr", 101_325.0),
    ],
)
def test_pressure_reference_points(value, unit, pascal):
    assert units.to_pascal(value, unit) == pytest.approx(pascal, rel=1e-12)
    assert units.from_pascal(pascal, unit) == pytest.approx(value, rel=1e-12)


@given(
    st.floats(min_value=1e-3, max_value=1e4),
    st.sampled_from(sorted(units.TEMPERATURE_UNITS)),
)
def test_temperature_round_trip(value, unit):
    assert units.to_kelvin(units.from_kelvin(value, unit), unit) == pytest.approx(value)


@given(
    st.floats(min_value=1e-6, max_value=1e10),
    st.sampled_from(sorted(units.PRESSURE_UNITS)),
)
def test_pressure_round_trip(value, unit):
    assert units.to_pascal(units.from_pascal(value, unit), unit) == pytest.approx(value)


def test_arrays_convert_elementwise():
    np.testing.assert_allclose(units.to_kelvin(np.array([0.0, 100.0]), "degC"), [273.15, 373.15])
    np.testing.assert_allclose(units.to_pascal(np.array([1.0, 2.0]), "bar"), [1e5, 2e5])


@pytest.mark.parametrize(
    "convert", [units.to_kelvin, units.from_kelvin, units.to_pascal, units.from_pascal]
)
def test_unknown_unit_is_rejected(convert):
    with pytest.raises(UnitError, match="unknown"):
        convert(1.0, "furlong")
