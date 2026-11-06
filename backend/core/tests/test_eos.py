import numpy as np
import pytest
from thermo.eos_mix import PRMIX, RKMIX, SRKMIX, VDWMIX

from pec.components import get_component
from pec.constants import R
from pec.eos import EOS, ln_phi, pressure

# A natural-gas-like mixture with nonzero k_ij (symmetric; values typical for these pairs)
COMPONENTS = [
    get_component(n) for n in ["Methane", "Ethane", "n-Butane", "Nitrogen", "CarbonDioxide"]
]
X = np.array([0.5, 0.2, 0.15, 0.05, 0.1])
KIJ = np.array(
    [
        [0.0, 0.003, 0.012, 0.03, 0.09],
        [0.003, 0.0, 0.01, 0.04, 0.13],
        [0.012, 0.01, 0.0, 0.08, 0.13],
        [0.03, 0.04, 0.08, 0.0, -0.02],
        [0.09, 0.13, 0.13, -0.02, 0.0],
    ]
)


def test_critical_point_is_a_triple_root():
    # At Tc, Pc every cubic has a triple root Z = Zc (vdW 3/8, RK and SRK 1/3, PR 0.30740).
    # A triple root is ill-conditioned: rounding of 1e-16 moves it by ~(1e-16)^(1/3) ≈ 1e-5.
    methane = get_component("Methane")
    Zc = {"vdW": 3 / 8, "RK": 1 / 3, "SRK": 1 / 3, "PR": 0.3074013086987}
    for eos in EOS:
        for phase in ("liquid", "vapour"):
            Z, _ = ln_phi(eos, [methane], methane.Tc, methane.Pc, [1.0], phase)
            assert Z == pytest.approx(Zc[eos], rel=1e-4)


@pytest.mark.parametrize(
    ("eos", "mix"), [("vdW", VDWMIX), ("RK", RKMIX), ("SRK", SRKMIX), ("PR", PRMIX)]
)
def test_matches_thermo(eos, mix):
    # Independent implementation (thermo, D-08). thermo's vdW fugacity uses 2√(a a_i), which is
    # right only for k_ij = 0, so vdW is compared without k_ij (the next test covers it).
    kij = np.zeros_like(KIJ) if eos == "vdW" else KIJ
    for T, P in [(200.0, 1e6), (350.0, 1e7)]:  # three roots; one root
        ref = mix(
            Tcs=[c.Tc for c in COMPONENTS],
            Pcs=[c.Pc for c in COMPONENTS],
            omegas=[c.omega for c in COMPONENTS],
            zs=list(X),
            kijs=kij.tolist(),
            T=T,
            P=P,
        )
        # thermo only sets Z_l / Z_g for the roots that exist
        for phase, Z_name, ln_phi_name in [
            ("liquid", "Z_l", "lnphis_l"),
            ("vapour", "Z_g", "lnphis_g"),
        ]:
            if hasattr(ref, Z_name):
                Z, ln_phi_i = ln_phi(eos, COMPONENTS, T, P, X, phase, kij)
                assert Z == pytest.approx(getattr(ref, Z_name), rel=1e-12)
                assert ln_phi_i == pytest.approx(getattr(ref, ln_phi_name), abs=1e-12)
        # With two candidate roots, "stable" must pick the one with the lower Gibbs energy
        if hasattr(ref, "Z_l") and hasattr(ref, "Z_g"):
            Z_stable = ref.Z_l if ref.G_dep_l < ref.G_dep_g else ref.Z_g
            Z, _ = ln_phi(eos, COMPONENTS, T, P, X, "stable", kij)
            assert Z == pytest.approx(Z_stable, rel=1e-12)


def test_ln_phi_is_derivative_of_gibbs_energy():
    # ln φ̂_i = ∂(n g^R/RT)/∂n_i at T, P, n_j, with g^R/RT = Σ x_i ln φ̂_i: checks the formula
    # itself, k_ij terms included, by central differences in the mole numbers.
    T, P, h = 250.0, 5e6, 1e-6

    def nG(eos, n):
        x = n / n.sum()
        return n.sum() * (x @ ln_phi(eos, COMPONENTS, T, P, x, kij=KIJ)[1])

    for eos in EOS:
        numeric = [(nG(eos, X + h * e) - nG(eos, X - h * e)) / (2 * h) for e in np.eye(len(X))]
        assert ln_phi(eos, COMPONENTS, T, P, X, kij=KIJ)[1] == pytest.approx(numeric, abs=1e-8)


def test_pressure_at_a_root_is_the_pressure():
    # The cubic in Z is the equation of state rearranged, so P(V = ZRT/P) must give back P.
    T, P = 200.0, 1e6
    for eos in EOS:
        for phase in ("liquid", "vapour"):
            Z, _ = ln_phi(eos, COMPONENTS, T, P, X, phase, KIJ)
            assert pressure(eos, COMPONENTS, T, Z * R * T / P, X, KIJ) == pytest.approx(P, rel=1e-9)
