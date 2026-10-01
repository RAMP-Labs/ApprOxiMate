"""Tests for approximate.capacity."""
import json
import sys
from pathlib import Path

import pytest

from approximate import capacity, molar_mass
from approximate.capacity import ATOMIC_MASS, FARADAY

# q_max and q_adj (mAh/g, 1 d.p.) from exp0_parity_plot_theo_cap.ipynb,
# i.e. the values in the paper (computed there with F = 96485).
PAPER_PARITY = [
    ("NaFe0.3Co0.7O2", 237.2, 166.0),
    ("NaFe0.4Co0.6O2", 237.8, 142.7),
    ("NaFe0.5Co0.5O2", 238.5, 119.2),
    ("NaFe0.6Co0.4O2", 239.2, 95.7),
    ("NaFe0.7Co0.3O2", 239.8, 71.9),
    ("NaFe1/3Co1/3Ni1/3O2", 237.6, 156.8),
    ("NaLi0.11Ti0.56Ni0.33O2", 263.0, 176.2),
    ("Na4NiTeO6", 286.5, 143.2),
    ("NaMg0.15Ti0.7Ni0.15O2", 265.5, 185.9),
    ("NaTi0.25Fe0.25Co0.25Ni0.25O2", 242.9, 182.2),
    ("NaTi0.33Fe0.33Ni0.33O2", 246.8, 155.5),
    ("NaFe0.5Ni0.5O2", 238.8, 119.4),
    ("NaCo0.15Ni0.8Al0.05O2", 239.0, 227.1),
    ("NaLi0.1Ti0.2Fe0.2Co0.2Ni0.2Sn0.1O2", 239.7, 119.8),
    ("NaLi0.05Mg0.05Ti0.45Ni0.3Cu0.1Si0.05O2", 259.1, 142.5),
    ("NaTiO2", 260.6, 260.6),
    ("NaTi0.9Al0.1O2", 266.0, 239.4),
    ("NaTi0.65Mg0.35O2", 283.3, 85.0),
    ("NaTi0.85Mg0.15O2", 269.8, 188.9),
    ("Na4FeRuO6 ", 310.9, 233.1),
    ("NaCo1/3Ni1/3Mn1/3O2", 238.2, 238.2),
    ("NaFe1/3Mn1/3Ni1/3O2", 240.4, 240.4),
    ("NaMnO2", 243.8, 243.8),
    ("NaNi0.12Cu0.12Mg0.12Fe0.15Co0.15Mn0.1Ti0.1Sn0.1Sb0.04O2", 229.4, 162.9),
]


@pytest.mark.parametrize("formula, q_max, q_adj", PAPER_PARITY)
def test_reproduces_paper_parity_values(formula, q_max, q_adj):
    c = capacity(formula, alkali="Na")
    assert round(c.q_theoretical, 1) == q_max
    assert round(c.q_adjusted, 1) == q_adj


def test_exact_faraday_constant():
    assert FARADAY == 96485.33212


def test_atomic_masses_match_mendeleev():
    mendeleev = pytest.importorskip("mendeleev")
    from mendeleev.fetch import fetch_table
    table = fetch_table("elements").set_index("symbol")["atomic_weight"]
    for el, mass in ATOMIC_MASS.items():
        assert mass == pytest.approx(table[el], abs=1e-6), el


def test_result_fields_are_consistent():
    c = capacity("NaFe0.5Co0.5O2")
    assert c.alkali == "Na"
    assert c.full == 1.0
    assert c.removable + c.remaining == pytest.approx(c.full)
    assert c.q_adjusted <= c.q_theoretical
    assert c.per_alkali == pytest.approx(FARADAY / (3.6 * c.molar_mass))
    assert set(c.to_dict()) >= {"q_theoretical", "q_adjusted", "removable"}


def test_molar_mass():
    assert molar_mass("NaCl") == pytest.approx(22.98976928 + 35.45)
    assert molar_mass({"Na": 1, "Cl": 1}) == molar_mass("NaCl")


def test_alkali_is_detected_automatically():
    assert capacity("LiFePO4").alkali == "Li"


def test_alkali_must_be_given_when_ambiguous():
    with pytest.raises(ValueError, match="Specify alkali"):
        capacity("LiNaFe2O4")


def test_errors():
    with pytest.raises(ValueError, match="not found"):
        capacity("LiFePO4", alkali="Na")
    with pytest.raises(ValueError, match="Could not parse"):
        capacity("NaXx2O")
    with pytest.raises(ValueError, match="No atomic mass"):
        molar_mass({"Na": 1, "Xx": 1})


# --- the website uses this through site/bridge.py --------------------------

@pytest.fixture
def bridge():
    sys.path.insert(0, str(Path(__file__).parents[1] / "site"))
    import bridge
    yield bridge
    sys.path.pop(0)


def test_bridge_capacity_matches_package(bridge):
    r = json.loads(bridge.capacity("NaFe0.5Co0.5O2", "Na"))
    c = capacity("NaFe0.5Co0.5O2", alkali="Na")
    assert r["ok"]
    assert r["q_max"] == c.q_theoretical and r["q_adj"] == c.q_adjusted
    assert set(r) == {"ok", "full", "removable", "remaining_at_limit",
                      "molar_mass", "per_unit", "q_max", "q_adj"}


def test_bridge_capacity_reports_errors(bridge):
    r = json.loads(bridge.capacity("LiFePO4", "Na"))
    assert r == {"ok": False, "error": "Na not found in formula"}
