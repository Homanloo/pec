import statistics

import pytest
from chemicals import Pc, Pc_methods, Tc, Tc_methods, omega, omega_methods
from chemicals.elements import molecular_weight, simple_formula_parser

from pec.components import COMPONENTS, get_component

# Independent tabulated data in `chemicals` (dev-only, D-08). HEOS is left out: it is CoolProp,
# our own source. Same tables and tolerances as scripts/make_components.py.
TC_PC_TABLES = {"IUPAC", "MATTHEWS", "CRC", "PD", "WEBBOOK", "PSRK", "PINAMARTINES", "YAWS"}
OMEGA_TABLES = {"PSRK", "PD", "YAWS"}


def median_of_tables(cas, value, methods, tables):
    # The median shrugs off a single bad table (e.g. the IUPAC row for cyclohexane in
    # chemicals 1.5.2 holds methylcyclopentane's values).
    return statistics.median(value(cas, method=m) for m in methods(cas) if m in tables)


def test_data_agrees_with_independent_tables():
    bad = []
    for c in COMPONENTS.values():
        Tc_ref = median_of_tables(c.cas, Tc, Tc_methods, TC_PC_TABLES)
        Pc_ref = median_of_tables(c.cas, Pc, Pc_methods, TC_PC_TABLES)
        omega_ref = median_of_tables(c.cas, omega, omega_methods, OMEGA_TABLES)
        # Molar mass from the formula (IUPAC atomic weights); also catches a wrong CAS number,
        # since the formula was looked up by CAS.
        M_ref = molecular_weight(simple_formula_parser(c.formula)) / 1000
        if not (
            abs(c.Tc / Tc_ref - 1) <= 0.01
            and abs(c.Pc / Pc_ref - 1) <= 0.05
            and abs(c.omega - omega_ref) <= 0.05
            and abs(c.molar_mass / M_ref - 1) <= 5e-4
        ):
            bad.append(c.name)
    assert bad == []


def test_get_component():
    methane = get_component("Methane")
    assert (methane.cas, methane.Tc, methane.Pc) == ("74-82-8", 190.564, 4599200)
    with pytest.raises(KeyError, match="unknown component"):
        get_component("methane")
