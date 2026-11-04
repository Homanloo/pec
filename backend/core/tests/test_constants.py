import pytest

from pec import constants


def test_gas_constant_is_the_exact_si_value():
    assert constants.R == pytest.approx(8.31446261815324, rel=1e-15)


def test_gas_constant_in_legacy_units():
    # 83.14462618 cm³ bar mol⁻¹ K⁻¹: the legacy code truncated it to 83.14.
    assert constants.R * 1e6 / constants.P_BAR == pytest.approx(83.14462618, rel=1e-9)
