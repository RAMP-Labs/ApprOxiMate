"""Plots of charge balance and oxidation states during alkali removal.

Needs matplotlib:  pip install "approximate[plot]"

Every function draws on `ax` if given (for multi-panel figures), otherwise
makes a new figure, and returns the axes. Nothing here changes your
matplotlib style; use your own rcParams or style sheet.

    >>> from approximate.plotting import plot_oxidation_states
    >>> ax = plot_oxidation_states("NaMnO2")
"""
try:
    import matplotlib.pyplot as plt
except ImportError as e:  # pragma: no cover
    raise ImportError(
        'approximate.plotting needs matplotlib: pip install "approximate[plot]"'
    ) from e

import numpy as np

from .sweep import _parsed, alkali_sweep

__all__ = [
    "plot_charge_balance",
    "plot_substitution",
    "plot_average_oxidation_states",
    "plot_oxidation_states",
]


def _get_ax(ax):
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 5))
    return ax


def _colors(n, cmap="viridis", cmap_range=(0.1, 0.9)):
    cmap = plt.get_cmap(cmap)
    lo, hi = cmap_range
    if n == 1:
        return [cmap((lo + hi) / 2)]
    return [cmap(lo + (hi - lo) * i / (n - 1)) for i in range(n)]


def plot_charge_balance(formula, alkali=None, interval=0.01, max_range=2.0,
                        ax=None, color="#e55c30"):
    """Residual charge vs alkali content."""
    ax = _get_ax(ax)
    s = alkali_sweep(formula, alkali, interval, max_range)
    ax.plot(s.values, s.final_charge, "o", markersize=4, color=color,
            label=f"{s.alkali} Charge Balance")
    ax.axhline(y=0, color="grey", linestyle="--", label="Charge Neutral Line", alpha=0.8)
    ax.set_xlabel(f"Amount of {s.alkali}")
    ax.set_ylabel("Charge Balance")
    ax.legend(loc="best")
    return ax


def plot_substitution(base_formula, metal_a, metal_b, fractions, alkali=None,
                      interval=0.01, max_range=2.0, ax=None, cmap="viridis"):
    """Charge balance vs alkali content as metal_b replaces metal_a.

    fractions: fraction of metal_a replaced by metal_b, e.g. np.linspace(0.1, 0.9, 9).
    """
    ax = _get_ax(ax)
    base = _parsed(base_formula)
    if metal_a not in base:
        raise ValueError(f"{metal_a} not found in base formula.")
    amount_a = base[metal_a]
    fractions = np.asarray(fractions)
    for frac, color in zip(fractions, _colors(len(fractions), cmap)):
        f = {**base, metal_a: amount_a * (1 - frac), metal_b: amount_a * frac}
        s = alkali_sweep(f, alkali, interval, max_range)
        ax.plot(s.values, s.final_charge, "o", markersize=4, color=color,
                label=f"{metal_a}{f[metal_a]:.2f}{metal_b}{f[metal_b]:.2f}")
    ax.axhline(0, color="gray", linestyle="--")
    ax.set_xlabel(f"Amount of {s.alkali}")
    ax.set_ylabel("Charge Balance")
    ax.legend(loc="best")
    return ax


def plot_average_oxidation_states(formula, alkali=None, interval=0.01, max_range=2.0,
                                  ax=None, cmap="viridis", cmap_range=(0.1, 0.9)):
    """Average oxidation state of each non-alkali, non-O element vs alkali content."""
    ax = _get_ax(ax)
    s = alkali_sweep(formula, alkali, interval, max_range)
    colors = _colors(len(s.average_oxidation_states), cmap, cmap_range)
    for (el, avg), color in zip(s.average_oxidation_states.items(), colors):
        ax.plot(s.values, avg, "o-", markersize=4, color=color, label=el,
                linewidth=2, alpha=0.6)
    ax.set_xlabel(f"Fractional amount of {s.alkali}")
    ax.set_ylabel("Average Oxidation State")
    ax.invert_xaxis()
    ax.legend(loc="best")
    return ax


def plot_oxidation_states(formula, alkali=None, interval=0.01, max_range=2.0,
                          ax=None, cmap="viridis", cmap_range=(0.1, 0.9)):
    """Amount of each element in each oxidation state vs alkali content."""
    ax = _get_ax(ax)
    s = alkali_sweep(formula, alkali, interval, max_range)
    items = sorted(s.oxidation_states.items())
    for ((el, ox), amounts), color in zip(items, _colors(len(items), cmap, cmap_range)):
        ax.plot(s.values, amounts, "o-", markersize=4, color=color,
                label=f"{el}$^{{{ox:+d}}}$", linewidth=2, alpha=0.6)
    ax.set_ylim(-0.03, 1.003)
    ax.set_xlabel(f"Fractional amount of {s.alkali}")
    ax.set_ylabel("Fractional amount for each oxidation state")
    ax.invert_xaxis()
    ax.legend(loc="best")
    return ax
