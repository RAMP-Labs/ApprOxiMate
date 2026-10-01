"""Tests for the new public functions."""
import warnings

import pandas as pd
import pytest

from approx.approximate import (
    BalanceResult, charge_balance, final_charge, oxidation_states, parse_formula,
)


def test_charge_balance_returns_result():
    r = charge_balance("Fe3O4")
    assert isinstance(r, BalanceResult)
    assert r.is_balanced and r.final_charge == 0.0
    assert str(r) == "O:-2:4.0;Fe:2:1.0;Fe:3:2.0;FinalChargeBalance:0.0"


def test_every_format_has_the_same_content():
    r = charge_balance("Na0.67Ni0.33Mn0.67O2")
    d, df = r.to_dict(), r.to_dataframe()
    assert d["final_charge"] == r.final_charge
    assert d["is_balanced"] == r.is_balanced
    assert len(d["elements"]) == len(df) == len(r.oxidation_states)


def test_split_element_appears_once_per_state():
    states = oxidation_states("Fe3O4")
    fe = sorted((s.oxidation_state, s.quantity) for s in states if s.element == "Fe")
    assert fe == [(2, 1.0), (3, 2.0)]


def test_oxidation_states_as_dataframe():
    df = oxidation_states("LiFePO4", as_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert set(df["Element"]) == {"Li", "Fe", "P", "O"}


def test_final_charge_shortcut():
    assert final_charge("NaCl") == 0.0
    assert final_charge("Na3O") == charge_balance("Na3O").final_charge


def test_parse_formula():
    assert parse_formula("LiFePO4") == {"Li": 1.0, "Fe": 1.0, "P": 1.0, "O": 4.0}


def test_unknown_element_returns_none():
    assert charge_balance("Xx2O") is None
    assert final_charge("Xx2O") is None
    assert oxidation_states("Xx2O") is None


def test_old_return_format_still_works_but_warns():
    from approx.approximate import ApprOXimate
    with pytest.warns(DeprecationWarning):
        s = ApprOXimate().charge_balance("Fe3O4", return_format="string")
    assert s == str(charge_balance("Fe3O4"))