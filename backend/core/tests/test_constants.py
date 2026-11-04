import pytest

from pec.constants import P_BAR, R


def test_gas_constant_in_cm3_bar():
    # Textbooks quote R = 83.14462618 cm³ bar/(mol K).
    assert R * 1e6 / P_BAR == pytest.approx(83.14462618, rel=1e-9)
