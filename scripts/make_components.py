"""Build backend/core/src/pec/components.json from the reference equations of state in CoolProp.

Run from the repo root (CoolProp and chemicals are not runtime dependencies; only this script
needs CoolProp):

    uv run --no-project --with coolprop==8.0.0 --with chemicals==1.5.2 \
        python scripts/make_components.py

Per fluid: Tc and Pc are the critical point of its reference equation of state; ω is
Pitzer's definition, ω = −log10(P^sat(0.7 Tc) / Pc) − 1 (Pitzer et al., 1955), evaluated with
the same equation, so the three values are consistent. CoolProp's own stored ω is not used: for
some fluids it disagrees with its equation (propylene glycol: 0.327 stored, 0.720 by definition).
The formula comes from `chemicals` (PubChem, looked up by CAS number).

A fluid is kept only if independent tables confirm it (same check as tests/test_components.py).
"""

import json
import math
import statistics
from pathlib import Path

import CoolProp.CoolProp as CP
from chemicals import Pc, Pc_methods, Tc, Tc_methods, omega, omega_methods, search_chemical

OUT = Path(__file__).parents[1] / "backend/core/src/pec/components.json"

# Tabulated (not estimated) data in `chemicals`; HEOS is left out because it is CoolProp itself.
TC_PC_TABLES = {"IUPAC", "MATTHEWS", "CRC", "PD", "WEBBOOK", "PSRK", "PINAMARTINES", "YAWS"}
OMEGA_TABLES = {"PSRK", "PD", "YAWS"}


def median_of_tables(cas, value, methods, tables):
    """Median over the independent tables that list this compound, or None if none do."""
    values = [value(cas, method=m) for m in methods(cas) if m in tables]
    return statistics.median(values) if values else None


def disagreement(cas, Tc_, Pc_, omega_):
    """Why the entry is not confirmed by the independent tables, or "" if it is."""
    Tc_ref = median_of_tables(cas, Tc, Tc_methods, TC_PC_TABLES)
    Pc_ref = median_of_tables(cas, Pc, Pc_methods, TC_PC_TABLES)
    omega_ref = median_of_tables(cas, omega, omega_methods, OMEGA_TABLES)
    if None in (Tc_ref, Pc_ref, omega_ref):
        return "no independent value"
    if abs(Tc_ / Tc_ref - 1) > 0.01:
        return f"Tc {Tc_:.2f} vs {Tc_ref:.2f} K"
    if abs(Pc_ / Pc_ref - 1) > 0.05:
        return f"Pc {Pc_ / 1e6:.3f} vs {Pc_ref / 1e6:.3f} MPa"
    if abs(omega_ - omega_ref) > 0.05:
        return f"ω {omega_:.3f} vs {omega_ref:.3f}"
    return ""


components = {}
for name in sorted(CP.get_global_param_string("FluidsList").split(","), key=str.lower):
    cas = CP.get_fluid_param_string(name, "CAS")
    # Skip pseudo-pure mixtures (Air, R404A, ...) and the ortho/para spin isomers of H2 and D2,
    # whose CAS numbers carry a letter suffix. None of them is a single component.
    if CP.get_fluid_param_string(name, "pure") != "true" or not cas[-1].isdigit():
        continue
    try:
        formula = search_chemical(cas).formula
    except ValueError:
        print(f"dropped {name}: CAS {cas} not in chemicals")
        continue

    Tc_ = CP.PropsSI("Tcrit", name)
    Pc_ = CP.PropsSI("pcrit", name)
    Psat = CP.PropsSI("P", "T", 0.7 * Tc_, "Q", 0, name)
    omega_ = -math.log10(Psat / Pc_) - 1

    why = disagreement(cas, Tc_, Pc_, omega_)
    if why:
        print(f"dropped {name}: {why}")
        continue

    components[name] = {
        "cas": cas,
        "formula": formula,
        "molar_mass": round(CP.PropsSI("molar_mass", name), 9),  # kg/mol
        "Tc": round(Tc_, 3),  # K
        "Pc": round(Pc_),  # Pa
        "omega": round(omega_, 5),
        "source": CP.get_fluid_param_string(name, "BibTeX-EOS"),  # key in CoolProp's .bib
    }

OUT.write_text(json.dumps(components, indent=1, ensure_ascii=False) + "\n")
print(f"{len(components)} components written to {OUT}")
