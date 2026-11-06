"""Pure-component data: critical constants and acentric factor.

The data in components.json comes from the reference equations of state collected in CoolProp
(Bell et al., 2014, Ind. Eng. Chem. Res. 53, 2498): Tc and Pc are each equation's critical
point, and ω is Pitzer's definition evaluated with the same equation (Pitzer et al., 1955,
J. Am. Chem. Soc. 77, 3433). How it was built and checked: scripts/make_components.py and
docs/science/components.md.
"""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Component:
    name: str  # CoolProp fluid name, e.g. "Methane", "n-Butane", "CarbonDioxide"
    cas: str
    formula: str
    molar_mass: float  # kg/mol
    Tc: float  # K
    Pc: float  # Pa
    omega: float  # acentric factor
    source: str  # BibTeX key of the reference equation of state in CoolProp's library


_data = json.loads((Path(__file__).parent / "components.json").read_text(encoding="utf-8"))
COMPONENTS = {name: Component(name=name, **entry) for name, entry in _data.items()}


def get_component(name):
    """Return the component with this CoolProp fluid name (case-sensitive)."""
    try:
        return COMPONENTS[name]
    except KeyError:
        raise KeyError(f"unknown component {name!r}") from None
