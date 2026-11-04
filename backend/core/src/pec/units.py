"""Temperature and pressure unit conversions to and from SI (K, Pa).

The core works in SI only; these helpers are for the boundaries (API, scripts). Every factor is
exact by definition: the international pound (0.45359237 kg) and inch (0.0254 m), standard
gravity (9.80665 m s⁻²), the conventional millimetre of mercury (13.5951 g cm⁻³ × g_n × 1 mm,
= 133.322387415 Pa) and the torr (101325/760 Pa).
"""

from collections.abc import Mapping
from types import MappingProxyType

import numpy as np
from numpy.typing import NDArray

from pec.constants import P_ATM, P_BAR, T_ZERO_CELSIUS
from pec.errors import UnitError

type Value = float | NDArray[np.float64]

_POUND_FORCE = 0.45359237 * 9.80665  # N
_PSI = _POUND_FORCE / 0.0254**2  # Pa

# T[K] = scale * value + offset
TEMPERATURE_UNITS: Mapping[str, tuple[float, float]] = MappingProxyType(
    {
        "K": (1.0, 0.0),
        "degC": (1.0, T_ZERO_CELSIUS),
        "degF": (5 / 9, T_ZERO_CELSIUS - 32 * 5 / 9),
        "degR": (5 / 9, 0.0),
    }
)
"""Supported temperature units and their affine map to kelvin."""

# P[Pa] = factor * value
PRESSURE_UNITS: Mapping[str, float] = MappingProxyType(
    {
        "Pa": 1.0,
        "kPa": 1.0e3,
        "MPa": 1.0e6,
        "bar": P_BAR,
        "atm": P_ATM,
        "psi": _PSI,
        "mmHg": 133.322387415,
        "torr": P_ATM / 760,
    }
)
"""Supported pressure units and their factor to pascal (absolute pressures only)."""


def _temperature(unit: str) -> tuple[float, float]:
    try:
        return TEMPERATURE_UNITS[unit]
    except KeyError:
        raise UnitError(
            f"unknown temperature unit {unit!r}; expected one of {sorted(TEMPERATURE_UNITS)}"
        ) from None


def _pressure(unit: str) -> float:
    try:
        return PRESSURE_UNITS[unit]
    except KeyError:
        raise UnitError(
            f"unknown pressure unit {unit!r}; expected one of {sorted(PRESSURE_UNITS)}"
        ) from None


def to_kelvin(value: Value, unit: str) -> Value:
    """Convert a temperature in `unit` to kelvin."""
    scale, offset = _temperature(unit)
    return scale * value + offset


def from_kelvin(value: Value, unit: str) -> Value:
    """Convert a temperature in kelvin to `unit`."""
    scale, offset = _temperature(unit)
    return (value - offset) / scale


def to_pascal(value: Value, unit: str) -> Value:
    """Convert an absolute pressure in `unit` to pascal."""
    return _pressure(unit) * value


def from_pascal(value: Value, unit: str) -> Value:
    """Convert an absolute pressure in pascal to `unit`."""
    return value / _pressure(unit)
