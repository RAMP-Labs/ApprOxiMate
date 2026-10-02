"""Tests for approximate.plotting (skipped if matplotlib is missing)."""
import numpy as np
import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from approximate import alkali_sweep  # noqa: E402
from approximate import plotting as P  # noqa: E402


@pytest.fixture(autouse=True)
def _close():
    yield
    plt.close("all")


def test_draws_on_given_axes_and_returns_it():
    fig, ax = plt.subplots()
    assert P.plot_charge_balance("NaCoO2", ax=ax) is ax


def test_makes_own_figure_without_ax():
    ax = P.plot_oxidation_states("NaMnO2")
    assert ax.figure is not None


def test_plotted_data_is_the_sweep_data():
    ax = P.plot_oxidation_states("NaCo0.5Fe0.5O2", interval=0.01, max_range=1.2)
    s = alkali_sweep("NaCo0.5Fe0.5O2", interval=0.01, max_range=1.2)
    for line, (_, amounts) in zip(ax.get_lines(), sorted(s.oxidation_states.items())):
        np.testing.assert_array_equal(line.get_ydata(), amounts)


def test_substitution_one_line_per_fraction_plus_zero_line():
    ax = P.plot_substitution("NaCoO2", "Co", "Fe", np.linspace(0.1, 0.9, 9))
    assert len(ax.get_lines()) == 10


def test_average_and_inverted_axis():
    ax = P.plot_average_oxidation_states("NaCo0.7Ni0.2Mn0.1O2")
    assert [l.get_label() for l in ax.get_lines()] == ["Co", "Mn", "Ni"]  # same order (and colours) as the paper figure
    assert ax.xaxis_inverted()


def test_does_not_change_global_style():
    before = dict(plt.rcParams)
    import importlib
    importlib.reload(P)
    P.plot_charge_balance("NaCoO2")
    assert dict(plt.rcParams) == before
