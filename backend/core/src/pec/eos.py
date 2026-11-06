"""Cubic equations of state: van der Waals, Redlich–Kwong, Soave–Redlich–Kwong, Peng–Robinson.

All four are one generic cubic (Smith, Van Ness & Abbott, 2005, §3.6 and Table 3.1):

    P = RT/(V − b) − a(T) / [(V + εb)(V + σb)]
    a_i = Ψ α(T_r, ω) R² Tc² / Pc,   b_i = Ω R Tc / Pc

Each equation is its constants (σ, ε, Ω, Ψ) plus an α function. Mixtures use the van der Waals
one-fluid rule with a k_ij matrix. Everything in SI. Full write-up: docs/science/cubic-eos.md.
"""

import math

import numpy as np

from pec.constants import R

# Ω and Ψ are the exact values implied by the critical conditions (∂P/∂V = ∂²P/∂V² = 0 at Tc, Pc);
# the papers print them rounded (PR: 0.07780 and 0.45724). η is b/Vc at the critical point.
_ETA_RK = 2 ** (1 / 3) - 1
_ETA_PR = 1 / (1 + (4 - 8**0.5) ** (1 / 3) + (4 + 8**0.5) ** (1 / 3))

# (σ, ε, Ω, Ψ) per equation
EOS = {
    "vdW": (0.0, 0.0, 1 / 8, 27 / 64),  # van der Waals (1873)
    "RK": (1.0, 0.0, _ETA_RK / 3, 1 / (9 * _ETA_RK)),  # Redlich & Kwong (1949)
    "SRK": (1.0, 0.0, _ETA_RK / 3, 1 / (9 * _ETA_RK)),  # Soave (1972)
    "PR": (  # Peng & Robinson (1976)
        1 + 2**0.5,
        1 - 2**0.5,
        _ETA_PR / (_ETA_PR + 3),
        8 * (5 * _ETA_PR + 1) / (49 - 37 * _ETA_PR),
    ),
}


def alpha(eos, Tr, omega):
    """α(T_r, ω) of each equation; T_r = T/Tc.

    vdW: 1. RK: T_r^(−1/2) (Redlich & Kwong, 1949).
    SRK: [1 + m(1 − √T_r)]², m = 0.480 + 1.574ω − 0.176ω² (Soave, 1972).
    PR:  [1 + κ(1 − √T_r)]², κ = 0.37464 + 1.54226ω − 0.26992ω² (Peng & Robinson, 1976).
    """
    match eos:
        case "vdW":
            return np.ones_like(Tr)
        case "RK":
            return 1 / np.sqrt(Tr)
        case "SRK":
            m = 0.480 + 1.574 * omega - 0.176 * omega**2
        case "PR":
            m = 0.37464 + 1.54226 * omega - 0.26992 * omega**2
        case _:
            raise ValueError(f"unknown equation of state {eos!r}")
    return (1 + m * (1 - np.sqrt(Tr))) ** 2


def z_roots(sigma, eps, A, B):
    """Real roots Z > B of the generic cubic in Z, in ascending order.

    Z³ + [(σ+ε−1)B − 1]Z² + [A + σεB² − (σ+ε)B(B+1)]Z − [AB + σεB²(B+1)] = 0,
    with A = aP/(RT)² and B = bP/(RT). Roots with Z ≤ B have V ≤ b and are not physical.
    Solved in closed form (Press et al., 2007, Numerical Recipes, 3rd ed., §5.6).
    """
    c2 = (sigma + eps - 1) * B - 1
    c1 = A + sigma * eps * B**2 - (sigma + eps) * B * (B + 1)
    c0 = -(A * B + sigma * eps * B**2 * (B + 1))

    Q = (c2**2 - 3 * c1) / 9
    Rc = (2 * c2**3 - 9 * c2 * c1 + 27 * c0) / 54
    if Rc**2 < Q**3:
        # Three real roots: trigonometric form
        theta = math.acos(Rc / Q**1.5)
        roots = [
            -2 * math.sqrt(Q) * math.cos((theta + k * 2 * math.pi) / 3) - c2 / 3 for k in (0, 1, -1)
        ]
    else:
        # One real root (or a multiple one, e.g. at the critical point, where S can be 0)
        S = -math.copysign((abs(Rc) + math.sqrt(Rc**2 - Q**3)) ** (1 / 3), Rc)
        roots = [S + (Q / S if S != 0 else 0.0) - c2 / 3]
    return sorted(Z for Z in roots if Z > B)


def _I(Z, B, sigma, eps):
    """I = ln[(Z + σB)/(Z + εB)] / (σ − ε); its limit B/(Z + εB) when σ = ε (vdW)."""
    if sigma == eps:
        return B / (Z + eps * B)
    return math.log((Z + sigma * B) / (Z + eps * B)) / (sigma - eps)


def ln_phi(eos, components, T, P, x, phase="stable", kij=None):
    """Compressibility factor Z and ln φ̂_i of a phase of mole fractions x at T [K], P [Pa].

    phase: "liquid" takes the smallest root, "vapour" the largest, "stable" the root with the
    lowest Gibbs energy. When the cubic has one real root, all three give it.
    kij: symmetric matrix of binary interaction parameters (default zeros).

    ln φ̂_i = (b_i/b)(Z − 1) − ln(Z − B) − (A/B)(2Σ_j x_j a_ij / a − b_i/b) I
    (Smith, Van Ness & Abbott, 2005, §14.4; Michelsen & Mollerup, 2007, ch. 3).
    """
    sigma, eps, Omega, Psi = EOS[eos]
    Tc = np.array([c.Tc for c in components])
    Pc = np.array([c.Pc for c in components])
    omega = np.array([c.omega for c in components])
    x = np.asarray(x, dtype=float)
    kij = np.zeros((len(x), len(x))) if kij is None else np.asarray(kij, dtype=float)

    # Pure-component parameters
    a_i = Psi * alpha(eos, T / Tc, omega) * (R * Tc) ** 2 / Pc
    b_i = Omega * R * Tc / Pc

    # van der Waals one-fluid mixing:
    # a = ΣΣ x_i x_j a_ij with a_ij = (1 − k_ij)√(a_i a_j);  b = Σ x_i b_i
    a_ij = (1 - kij) * np.sqrt(np.outer(a_i, a_i))
    sum_xa = a_ij @ x  # Σ_j x_j a_ij
    a = float(x @ sum_xa)
    b = float(x @ b_i)
    A = a * P / (R * T) ** 2
    B = b * P / (R * T)

    roots = z_roots(sigma, eps, A, B)
    if not roots:
        raise ArithmeticError(f"no root Z > B (A={A}, B={B}); check T, P and x")
    if phase == "liquid":
        Z = roots[0]
    elif phase == "vapour":
        Z = roots[-1]
    elif phase == "stable":
        # Residual Gibbs energy of the phase, g^R/RT = Σ x_i ln φ̂_i = Z − 1 − ln(Z − B) − (A/B) I;
        # same T, P and x for every root, so the lowest one is the stable root.
        Z = min(roots, key=lambda Z: Z - 1 - math.log(Z - B) - A / B * _I(Z, B, sigma, eps))
    else:
        raise ValueError(f"phase must be 'liquid', 'vapour' or 'stable', not {phase!r}")

    I = _I(Z, B, sigma, eps)  # noqa: E741 (the integral's usual symbol)
    ln_phi_i = b_i / b * (Z - 1) - math.log(Z - B) - A / B * (2 * sum_xa / a - b_i / b) * I
    return Z, ln_phi_i
