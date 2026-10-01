"""Tests for approximate.sweep (no matplotlib needed)."""
import numpy as np
import pytest

from approximate import alkali_sweep, charge_balance


def test_default_grid():
    s = alkali_sweep("NaMnO2", interval=0.01)
    assert s.alkali == "Na"
    np.testing.assert_array_equal(s.values, np.arange(0.01, 1.0, 0.01))


def test_final_charge_matches_charge_balance():
    s = alkali_sweep("NaCo0.5Fe0.5O2", values=[0.2, 0.5, 0.9])
    for x, q in zip(s.values, s.final_charge):
        assert q == charge_balance({"Na": x, "Co": 0.5, "Fe": 0.5, "O": 2}).final_charge


def test_states_sum_to_element_amount():
    s = alkali_sweep("NaCo0.7Ni0.2Mn0.1O2", interval=0.05)
    for el, total in {"Co": 0.7, "Ni": 0.2, "Mn": 0.1}.items():
        summed = sum(q for (e, _), q in s.oxidation_states.items() if e == el)
        np.testing.assert_allclose(summed, total)


def test_state_appearing_mid_sweep_is_in_the_right_place():
    # Co3+ only appears below Na ~ 0.5 in NaCo0.5Fe0.5O2 (regression test for
    # the old plotting code, which put its first point at the start)
    s = alkali_sweep("NaCo0.5Fe0.5O2", interval=0.01)
    co3 = s.oxidation_states[("Co", 3)]
    first = np.argmax(co3 > 0)
    assert first > 0 and np.all(co3[:first] == 0)
    r = charge_balance({"Na": s.values[first], "Co": 0.5, "Fe": 0.5, "O": 2})
    expected = sum(st.quantity for st in r.oxidation_states
                   if st.element == "Co" and st.oxidation_state == 3)
    assert co3[first] == pytest.approx(expected)


def test_average_oxidation_state():
    s = alkali_sweep("NaMnO2", values=[0.5])
    assert s.average_oxidation_states["Mn"][0] == pytest.approx(3.5)


def test_alkali_and_oxygen_excluded_by_default():
    s = alkali_sweep("NaMnO2", values=[0.5])
    assert {e for e, _ in s.oxidation_states} == {"Mn"}


def test_dataframe():
    df = alkali_sweep("NaMnO2", values=[0.25, 0.5]).to_dataframe()
    assert list(df.columns[:3]) == ["Na", "final_charge", "Mn_avg"]
    assert len(df) == 2
