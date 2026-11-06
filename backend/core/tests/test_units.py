import pytest

from pec import units


@pytest.mark.parametrize(
    ("value", "unit", "kelvin"),
    [
        (300.0, "K", 300.0),
        (100.0, "degC", 373.15),
        (212.0, "degF", 373.15),
        (-40.0, "degF", 233.15),  # -40 °F is also -40 °C
        (491.67, "degR", 273.15),
    ],
)
def test_temperature(value, unit, kelvin):
    assert units.to_kelvin(value, unit) == pytest.approx(kelvin)
    assert units.from_kelvin(kelvin, unit) == pytest.approx(value)


@pytest.mark.parametrize(
    ("value", "unit", "pascal"),
    [
        (1.0, "Pa", 1.0),
        (1.0, "kPa", 1e3),
        (1.0, "MPa", 1e6),
        (1.0, "bar", 1e5),
        (1.0, "atm", 101_325.0),
        (1.0, "psi", 6894.757293168361),
        (760.0, "mmHg", 101_325.0144354),
        (760.0, "torr", 101_325.0),
    ],
)
def test_pressure(value, unit, pascal):
    assert units.to_pascal(value, unit) == pytest.approx(pascal)
    assert units.from_pascal(pascal, unit) == pytest.approx(value)


def test_unknown_unit():
    with pytest.raises(KeyError):
        units.to_kelvin(1.0, "furlong")
