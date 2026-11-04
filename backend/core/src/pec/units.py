"""Convert temperature and pressure to and from SI (K, Pa).

Only used at the edges (API, scripts); the calculations themselves are always in SI.
"""

from pec.constants import P_ATM, P_BAR, T_ZERO_CELSIUS

# T[K] = scale * value + offset
TEMPERATURE_UNITS = {
    "K": (1.0, 0.0),
    "degC": (1.0, T_ZERO_CELSIUS),
    "degF": (5 / 9, T_ZERO_CELSIUS - 32 * 5 / 9),
    "degR": (5 / 9, 0.0),
}

# P[Pa] = factor * value. Absolute pressures only.
PRESSURE_UNITS = {
    "Pa": 1.0,
    "kPa": 1.0e3,
    "MPa": 1.0e6,
    "bar": P_BAR,
    "atm": P_ATM,
    "psi": 0.45359237 * 9.80665 / 0.0254**2,  # lbf/in², exact from the pound and inch
    "mmHg": 133.322387415,  # conventional mmHg, not exactly 1/760 atm
    "torr": P_ATM / 760,
}


def to_kelvin(value, unit):
    scale, offset = TEMPERATURE_UNITS[unit]
    return scale * value + offset


def from_kelvin(value, unit):
    scale, offset = TEMPERATURE_UNITS[unit]
    return (value - offset) / scale


def to_pascal(value, unit):
    return PRESSURE_UNITS[unit] * value


def from_pascal(value, unit):
    return value / PRESSURE_UNITS[unit]
