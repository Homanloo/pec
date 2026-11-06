import numpy as np
import pytest
from thermo import (
    CEOSGas,
    CEOSLiquid,
    ChemicalConstantsPackage,
    FlashVL,
    HeatCapacityGas,
    PropertyCorrelationsPackage,
)
from thermo.eos_mix import PRMIX, SRKMIX

from pec import equilibrium as eq
from pec.components import get_component
from pec.eos import ln_phi

# C1–C5 natural-gas liquid with two nonzero k_ij
COMPONENTS = [get_component(n) for n in ["Methane", "Ethane", "n-Propane", "n-Butane", "n-Pentane"]]
Z = np.array([0.4, 0.2, 0.15, 0.15, 0.1])
KIJ = np.zeros((5, 5))
KIJ[0, 4] = KIJ[4, 0] = 0.02
KIJ[0, 3] = KIJ[3, 0] = 0.01
THERMO = {"PR": PRMIX, "SRK": SRKMIX}


def thermo_flasher(eos):
    # thermo's own φ–φ flash (D-08) with the same data and k_ij. Its gas heat capacities are
    # needed only to build the object; TP and VF flashes do not use them.
    consts = ChemicalConstantsPackage(
        Tcs=[c.Tc for c in COMPONENTS],
        Pcs=[c.Pc for c in COMPONENTS],
        omegas=[c.omega for c in COMPONENTS],
        MWs=[c.molar_mass * 1000 for c in COMPONENTS],
        CASs=[c.cas for c in COMPONENTS],
    )
    cp = [HeatCapacityGas(CASRN=c.cas) for c in COMPONENTS]
    props = PropertyCorrelationsPackage(constants=consts, HeatCapacityGases=cp, skip_missing=True)
    kw = {"Tcs": consts.Tcs, "Pcs": consts.Pcs, "omegas": consts.omegas, "kijs": KIJ.tolist()}
    liquid = CEOSLiquid(THERMO[eos], kw, HeatCapacityGases=cp)
    gas = CEOSGas(THERMO[eos], kw, HeatCapacityGases=cp)
    return FlashVL(consts, props, liquid=liquid, gas=gas)


@pytest.mark.parametrize("eos", THERMO)
def test_flash(eos):
    ref = thermo_flasher(eos)
    # Two phases, the second near the mixture's critical region
    for T, P in [(300.0, 3e6), (320.0, 8e6)]:
        r = ref.flash(T=T, P=P, zs=list(Z))
        V, x, y = eq.flash(eos, COMPONENTS, T, P, Z, KIJ)
        # thermo converges to ~1e-7 (its fugacities agree only that well), so compare at 1e-6
        assert V == pytest.approx(r.VF, abs=1e-6)
        assert x == pytest.approx(r.liquid0.zs, abs=1e-6)
        assert y == pytest.approx(r.gas.zs, abs=1e-6)
        # Our own solution: equal fugacities, mass balance, normalised phases
        ln_f_L = np.log(x) + ln_phi(eos, COMPONENTS, T, P, x, "stable", KIJ)[1]
        ln_f_V = np.log(y) + ln_phi(eos, COMPONENTS, T, P, y, "stable", KIJ)[1]
        assert ln_f_L == pytest.approx(ln_f_V, abs=1e-9)
        assert V * y + (1 - V) * x == pytest.approx(Z, abs=1e-12)
        assert (x.sum(), y.sum()) == pytest.approx((1, 1), abs=1e-12)
    # One phase: superheated vapour and compressed liquid
    for T, P in [(350.0, 1e6), (300.0, 1.5e7)]:
        assert ref.flash(T=T, P=P, zs=list(Z)).phase_count == 1
        assert eq.flash(eos, COMPONENTS, T, P, Z, KIJ) is None


@pytest.mark.parametrize("eos", THERMO)
def test_bubble_and_dew_points(eos):
    ref = thermo_flasher(eos)
    # The 300 K bubble point (8.6 MPa) is near-critical: Wilson's start collapses to K = 1 and
    # the solver has to restart from below.
    cases = [
        (eq.bubble_pressure, 300.0, {"T": 300.0, "VF": 0}, "P"),
        (eq.dew_pressure, 300.0, {"T": 300.0, "VF": 1}, "P"),
        (eq.bubble_temperature, 3e6, {"P": 3e6, "VF": 0}, "T"),
        (eq.dew_temperature, 3e6, {"P": 3e6, "VF": 1}, "T"),
    ]
    for solve, given, spec, unknown in cases:
        r = ref.flash(zs=list(Z), **spec)
        value, incipient = solve(eos, COMPONENTS, given, Z, KIJ)
        assert value == pytest.approx(getattr(r, unknown), rel=1e-9)
        incipient_ref = r.gas.zs if spec["VF"] == 0 else r.liquid0.zs
        assert incipient == pytest.approx(incipient_ref, abs=1e-5)


def test_no_dew_point_above_the_cricondentherm():
    # At 450 K this mixture is vapour at every pressure: there is no dew point to find,
    # and the solver must say so rather than return the trivial solution.
    with pytest.raises(RuntimeError, match="dew point not found"):
        eq.dew_pressure("PR", COMPONENTS, 450.0, Z, KIJ)
