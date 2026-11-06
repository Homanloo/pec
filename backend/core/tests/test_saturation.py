import CoolProp.CoolProp as CP
import pytest
from thermo.eos import PR, RK, SRK, VDW

from pec.components import get_component
from pec.saturation import saturation_pressure

THERMO = {"vdW": VDW, "RK": RK, "SRK": SRK, "PR": PR}


@pytest.mark.parametrize("eos", THERMO)
def test_matches_thermo(eos):
    # Independent implementation (thermo, D-08), from deep in the liquid range (P^sat ~ 1e-3 Pa
    # for n-decane at T_r = 0.3, where tiny liquid roots must stay accurate) to next to Tc.
    for name in ("Methane", "n-Decane", "Water"):
        c = get_component(name)
        for Tr in (0.3, 0.7, 0.9999):
            T = Tr * c.Tc
            ref = THERMO[eos](Tc=c.Tc, Pc=c.Pc, omega=c.omega, T=T, P=1e5).Psat(T, polish=True)
            assert saturation_pressure(eos, c, T) == pytest.approx(ref, rel=1e-9)


def test_close_to_reference_equations():
    # Model check against the reference equations of state (CoolProp; NIST-quality P^sat).
    # ω is defined at T_r = 0.7 and Soave (1972) fitted m(ω) there, so SRK is within 0.1 %;
    # Peng & Robinson (1976) fitted κ(ω) over the whole range, so PR is within 1 %.
    for name in ["Methane", "Ethane", "n-Butane", "n-Decane", "Benzene", "Nitrogen", "Argon"]:
        c = get_component(name)
        T = 0.7 * c.Tc
        ref = CP.PropsSI("P", "T", T, "Q", 0, name)
        assert saturation_pressure("SRK", c, T) == pytest.approx(ref, rel=1e-3)
        assert saturation_pressure("PR", c, T) == pytest.approx(ref, rel=1e-2)


def test_no_saturation_at_or_above_tc():
    methane = get_component("Methane")
    with pytest.raises(ValueError, match="not below Tc"):
        saturation_pressure("PR", methane, methane.Tc)
