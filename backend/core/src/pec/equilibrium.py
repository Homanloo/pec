"""Vapour–liquid equilibrium of mixtures with a cubic equation of state (φ–φ).

Rachford–Rice, Michelsen's stability test, the isothermal (TP) flash, and bubble and dew
points in P or T. Every loop has an iteration limit and a tolerance and raises when it does not
converge; a solution that collapses to K = 1 (the trivial solution) is an error, never a result.
Mole fractions must be positive (drop absent components before calling).
Write-up: docs/science/equilibrium.md.
"""

import math

import numpy as np
from scipy.optimize import brentq

from pec.constants import R
from pec.eos import VC_OVER_B, ln_phi, mixture_parameters

TOL = 1e-10  # on ln K, ln W and ln ΣKx: equal fugacities to ~1e-10 relative
TRIVIAL = 1e-4  # max |ln K| below this means the two phases are the same phase
MAX_ITER = 1000


def wilson_K(components, T, P):
    """Wilson's K estimate: ln K_i = ln(Pc_i/P) + 5.373(1 + ω_i)(1 − Tc_i/T) (Wilson, 1969)."""
    Tc = np.array([c.Tc for c in components])
    Pc = np.array([c.Pc for c in components])
    omega = np.array([c.omega for c in components])
    return Pc / P * np.exp(5.373 * (1 + omega) * (1 - Tc / T))


def phase_label(eos, components, T, P, z, kij=None):
    """ "liquid" or "vapour" for a single (stable) phase.

    Vapour-like if its molar volume exceeds the pseudo-critical volume Σ z_i V_c,i of the EOS,
    with V_c,i = b_i·(V_c/b); since b = Σ z_i b_i this is V/b > V_c/b, i.e. Z/B > V_c/b. For a
    pure component below Tc it is exact (the liquid branch lies at V < Vc); for a mixture or a
    supercritical fluid it is a convention, not a phase boundary.
    """
    Z, _ = ln_phi(eos, components, T, P, z, "stable", kij)
    _, b, _, _ = mixture_parameters(eos, components, T, z, kij)
    return "vapour" if Z / (b * P / (R * T)) > VC_OVER_B[eos] else "liquid"


def rachford_rice(z, K):
    """Vapour fraction V with Σ z_i(K_i − 1)/(1 + V(K_i − 1)) = 0 (Rachford & Rice, 1952).

    The sum falls monotonically between its poles V_min = 1/(1 − K_max) and
    V_max = 1/(1 − K_min), where every 1 + V(K_i − 1) > 0, so the root there is unique and
    Brent's method cannot miss it. V may fall outside [0, 1] (negative flash; Whitson &
    Michelsen, 1989).
    """
    z, K = np.asarray(z, dtype=float), np.asarray(K, dtype=float)
    if not K.max() > 1 > K.min():
        raise ValueError("Rachford–Rice needs K_max > 1 > K_min")

    def g(V):
        return float(z @ ((K - 1) / (1 + V * (K - 1))))

    V_min, V_max = 1 / (1 - K.max()), 1 / (1 - K.min())
    margin = 1e-12 * (V_max - V_min)
    return brentq(g, V_min + margin, V_max - margin, xtol=1e-14, maxiter=200)


def stability_test(eos, components, T, P, z, kij=None):
    """Michelsen (1982a) tangent-plane stability test of the feed z at T, P.

    Returns None if z is stable (one phase), else K-values to start a flash from.
    Two trial phases from Wilson's K (vapour-like z·K and liquid-like z/K) are relaxed by
    successive substitution, ln W_i ← ln z_i + ln φ_i(z) − ln φ_i(w), w = W/ΣW. At the
    stationary point the tangent-plane distance is tm = 1 − ΣW; ΣW > 1 means unstable.
    """
    z = np.asarray(z, dtype=float)
    d = np.log(z) + ln_phi(eos, components, T, P, z, "stable", kij)[1]
    K_wilson = wilson_K(components, T, P)

    best_sum, best_K = 1.0, None
    for vapour_like in (True, False):
        lnW = np.log(z * K_wilson if vapour_like else z / K_wilson)
        for _ in range(MAX_ITER):
            w = np.exp(lnW) / np.exp(lnW).sum()
            lnW_new = d - ln_phi(eos, components, T, P, w, "stable", kij)[1]
            converged = np.max(np.abs(lnW_new - lnW)) < TOL
            lnW = lnW_new
            if converged:
                break
        else:
            raise RuntimeError(f"stability test did not converge in {MAX_ITER} iterations")

        W_sum = np.exp(lnW).sum()
        w = np.exp(lnW) / W_sum
        trivial = np.max(np.abs(np.log(w / z))) < TRIVIAL  # the trial phase fell back onto z
        if not trivial and W_sum > 1 + 1e-8 and W_sum > best_sum:
            best_sum, best_K = W_sum, (w / z if vapour_like else z / w)
    return best_K


def flash(eos, components, T, P, z, kij=None):
    """Isothermal flash of feed z at T [K], P [Pa] (Michelsen, 1982b).

    Returns None if the feed is one stable phase, else (V, x, y): vapour mole fraction and
    the liquid and vapour compositions. Stability test first; if unstable, successive
    substitution K_i = φ_i^L(x)/φ_i^V(y) from the stability test's K, with Rachford–Rice for V.
    """
    z = np.asarray(z, dtype=float)
    K = stability_test(eos, components, T, P, z, kij)
    if K is None:
        return None

    lnK = np.log(K)
    for _ in range(MAX_ITER):
        V = rachford_rice(z, np.exp(lnK))
        x = z / (1 + V * (np.exp(lnK) - 1))
        x /= x.sum()
        y = np.exp(lnK) * x
        y /= y.sum()
        lnK_new = (
            ln_phi(eos, components, T, P, x, "stable", kij)[1]
            - ln_phi(eos, components, T, P, y, "stable", kij)[1]
        )
        converged = np.max(np.abs(lnK_new - lnK)) < TOL
        lnK = lnK_new
        if converged:
            break
    else:
        raise RuntimeError(f"flash did not converge in {MAX_ITER} iterations")

    if np.max(np.abs(lnK)) < TRIVIAL:
        raise RuntimeError("flash converged to the trivial solution (K = 1)")
    if not 0 < V < 1:
        raise RuntimeError(f"flash converged to V = {V}, outside (0, 1)")
    return V, x, y


def bubble_pressure(eos, components, T, x, kij=None):
    """Bubble-point pressure [Pa] of liquid x at T [K], and the incipient vapour y."""
    _, P, y = _saturation_point(eos, components, x, kij, "bubble", T, None)
    return P, y


def dew_pressure(eos, components, T, y, kij=None):
    """Dew-point pressure [Pa] of vapour y at T [K], and the incipient liquid x."""
    _, P, x = _saturation_point(eos, components, y, kij, "dew", T, None)
    return P, x


def bubble_temperature(eos, components, P, x, kij=None):
    """Bubble-point temperature [K] of liquid x at P [Pa], and the incipient vapour y."""
    T, _, y = _saturation_point(eos, components, x, kij, "bubble", None, P)
    return T, y


def dew_temperature(eos, components, P, y, kij=None):
    """Dew-point temperature [K] of vapour y at P [Pa], and the incipient liquid x."""
    T, _, x = _saturation_point(eos, components, y, kij, "dew", None, P)
    return T, x


def _saturation_point(eos, components, z, kij, kind, T, P):
    """Bubble (z is the liquid) or dew (z is the vapour) point at fixed T or fixed P.

    Successive substitution on K_i = φ_i^L/φ_i^V with the incipient phase w from K; the unknown
    is updated by a Newton step on ln S = 0, S = Σ z_i K_i (bubble) or Σ z_i/K_i (dew), using
    Wilson's K for the derivative (K ∝ 1/P; ln K linear in 1/T, slope −a_i = −5.373(1 + ω_i)Tc_i),
    with each step capped. The liquid takes the liquid root and the vapour the vapour root.

    Near the critical region, a start on the dense side (P or bubble T too high, dew T too low)
    collapses to the trivial solution K = 1. Then the start moves away from the dense side and
    the solve is repeated; only a converged, non-trivial solution is ever returned.
    """
    z = np.asarray(z, dtype=float)
    sign = 1 if kind == "bubble" else -1  # bubble: S = Σ z K; dew: S = Σ z/K
    solve_P = P is None

    # Wilson's estimate, for which the bubble/dew condition can be solved directly
    if solve_P:
        KP = wilson_K(components, T, 1.0)  # Wilson's K·P
        P = float(z @ KP) if sign > 0 else 1 / float(z @ (1 / KP))
    else:
        T = brentq(
            lambda T: math.log(z @ wilson_K(components, T, P) ** sign),
            0.1 * min(c.Tc for c in components),
            10 * max(c.Tc for c in components),
        )

    for _ in range(10):
        result = _substitution(eos, components, z, kij, sign, T, P, solve_P)
        if result is not None:
            return result
        if solve_P:
            P *= 0.5
        else:
            T *= 0.95 if sign > 0 else 1.05
    raise RuntimeError(f"{kind} point not found: no non-trivial solution from 10 starts")


def _substitution(eos, components, z, kij, sign, T, P, solve_P):
    """One bubble/dew solve from (T, P): (T, P, w), or None if it ends at K = 1 or diverges."""
    a = np.array([5.373 * (1 + c.omega) * c.Tc for c in components])
    lnK = np.log(wilson_K(components, T, P))
    for _ in range(MAX_ITER):
        w = z * np.exp(sign * lnK)
        w /= w.sum()  # incipient phase from the current K
        x, y = (z, w) if sign > 0 else (w, z)
        lnK_new = (
            ln_phi(eos, components, T, P, x, "liquid", kij)[1]
            - ln_phi(eos, components, T, P, y, "vapour", kij)[1]
        )
        dlnK = float(np.max(np.abs(lnK_new - lnK)))
        lnK = lnK_new
        lnS = math.log(z @ np.exp(sign * lnK))
        if abs(lnS) < TOL and dlnK < TOL:
            break
        # Newton step on ln S = 0 with Wilson's derivative, capped at 20 % in P or 5 % in T
        if solve_P:
            P *= math.exp(np.clip(sign * lnS, -0.2, 0.2))
        else:
            T *= math.exp(np.clip(-sign * lnS * T / float(w @ a), -0.05, 0.05))
    else:
        return None
    if np.max(np.abs(lnK)) < TRIVIAL:
        return None
    w = z * np.exp(sign * lnK)
    return T, P, w / w.sum()
