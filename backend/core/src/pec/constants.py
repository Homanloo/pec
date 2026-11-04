"""Physical constants in SI units.

Exact values from the 2019 redefinition of the SI (BIPM, *The International System of Units*,
9th ed., 2019; CODATA 2018). All of PEC's core works in SI: K, Pa, mol, m³, J.
"""

from typing import Final

AVOGADRO: Final = 6.02214076e23
"""Avogadro constant N_A [mol⁻¹] (exact)."""

BOLTZMANN: Final = 1.380649e-23
"""Boltzmann constant k_B [J K⁻¹] (exact)."""

R: Final = AVOGADRO * BOLTZMANN
"""Molar gas constant R = N_A k_B = 8.31446261815324 J mol⁻¹ K⁻¹ (exact)."""

T_ZERO_CELSIUS: Final = 273.15
"""0 °C in kelvin [K] (exact by definition)."""

P_ATM: Final = 101_325.0
"""Standard atmosphere [Pa] (exact by definition)."""

P_BAR: Final = 1.0e5
"""One bar [Pa] (exact by definition)."""
