"""Vapour pressure of a pure component from a cubic equation of state.

P^sat(T) is the pressure where liquid and vapour roots have equal fugacity, ln φ^L = ln φ^V.
Between the two spinodal pressures (where ∂P/∂V = 0) the cubic has three roots, and there
f(P) = ln φ^L − ln φ^V is strictly monotonic: ∂f/∂ln P = Z^L − Z^V < 0. So P^sat is bracketed by
the spinodals and found with Brent's method, for any T < Tc, with no initial guess.
Write-up: docs/science/saturation.md.
"""

import math

from numpy.polynomial import Polynomial
from scipy.optimize import brentq

from pec.constants import R
from pec.eos import EOS, alpha, ln_phi


def saturation_pressure(eos, component, T):
    """Vapour pressure P^sat [Pa] of a pure component at T [K] (T < Tc)."""
    if T >= component.Tc:
        raise ValueError(f"T = {T} K is not below Tc = {component.Tc} K: no saturation")
    sigma, eps, Omega, Psi = EOS[eos]
    Tr = T / component.Tc

    # Spinodals in reduced volume v = V/b. With θ = a/(bRT) = Ψα/(Ω T_r) and
    # n(v) = v² + (σ+ε)v + σε, the EOS is P = (RT/b)[1/(v − 1) − θ/n(v)], and ∂P/∂V = 0 gives
    # n(v)² − θ(2v + σ + ε)(v − 1)² = 0. Below Tc it has two roots with v > 1.
    theta = Psi * float(alpha(eos, Tr, component.omega)) / (Omega * Tr)
    v = Polynomial([0.0, 1.0])
    n = v**2 + (sigma + eps) * v + sigma * eps
    roots = (n**2 - theta * (2 * v + sigma + eps) * (v - 1) ** 2).roots()
    v_spin = sorted(r.real for r in roots if abs(r.imag) <= 1e-9 * abs(r) and r.real > 1)
    if len(v_spin) < 2:
        raise ArithmeticError(f"no spinodals found at T = {T} K (too close to Tc?)")

    b = Omega * R * component.Tc / component.Pc
    P_liquid_spinodal = R * T / b * (1 / (v_spin[0] - 1) - theta / n(v_spin[0]))
    P_vapour_spinodal = R * T / b * (1 / (v_spin[-1] - 1) - theta / n(v_spin[-1]))

    def f(lnP):
        P = math.exp(lnP)
        return (
            ln_phi(eos, [component], T, P, [1.0], "liquid")[1][0]
            - ln_phi(eos, [component], T, P, [1.0], "vapour")[1][0]
        )

    # Stay just inside the spinodals, where both roots surely exist. The lower end is found by
    # stepping down from the top (one e-fold per step) until f > 0, never below the liquid
    # spinodal; at low T that spinodal is at negative pressure and gives no bound.
    hi = math.log(P_vapour_spinodal) - 1e-6
    floor = math.log(P_liquid_spinodal) + 1e-6 if P_liquid_spinodal > 0 else -math.inf
    lo = hi
    for _ in range(100):
        lo = max(lo - 1.0, floor)
        if f(lo) > 0 or lo == floor:
            break
    if not f(lo) > 0 > f(hi):
        raise ArithmeticError(f"P^sat not bracketed at T = {T} K")
    return math.exp(brentq(f, lo, hi, xtol=1e-13, rtol=1e-13, maxiter=200))
