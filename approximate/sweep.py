"""How charge balance and oxidation states change as alkali is removed.

No plotting here (see approximate.plotting for that), so this works
without matplotlib.

    >>> from approximate import alkali_sweep
    >>> s = alkali_sweep("NaMnO2")
    >>> s.to_dataframe().head()
"""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .capacity import ALKALI_METALS, _pick_alkali
from .core import charge_balance, parse_formula

#: Elements left out of the oxidation-state traces by default.
DEFAULT_EXCLUDE = frozenset(ALKALI_METALS) | {"O"}


@dataclass
class SweepResult:
    """Charge balance and oxidation states along an alkali sweep.

    Attributes:
        formula: the starting formula as {element: amount}.
        alkali: the alkali metal being varied.
        values: alkali amounts evaluated (ascending).
        final_charge: residual charge at each value (NaN if it failed).
        oxidation_states: {(element, ox_state): amounts}, the amount of each
            element in each oxidation state at every value (0 where absent).
        average_oxidation_states: {element: weighted mean oxidation state}.
    """
    formula: dict
    alkali: str
    values: np.ndarray
    final_charge: np.ndarray
    oxidation_states: dict = field(default_factory=dict)
    average_oxidation_states: dict = field(default_factory=dict)

    def to_dataframe(self) -> pd.DataFrame:
        """One row per alkali value; oxidation states as e.g. 'Mn+3' columns."""
        df = pd.DataFrame({self.alkali: self.values, "final_charge": self.final_charge})
        for el, avg in self.average_oxidation_states.items():
            df[f"{el}_avg"] = avg
        for (el, ox), amounts in sorted(self.oxidation_states.items()):
            df[f"{el}{ox:+d}"] = amounts
        return df


def _parsed(formula):
    if isinstance(formula, dict):
        return dict(formula)
    p = parse_formula(str(formula).strip())
    if not p:
        raise ValueError(f"Could not parse formula {formula!r} (unknown element?)")
    return p


def alkali_values(amount, interval=0.01, max_range=2.0):
    """Default grid: from `interval` up to (not including) min(amount, max_range)."""
    return np.arange(interval, min(amount, max_range), interval)


def alkali_sweep(formula, alkali=None, interval=0.01, max_range=2.0,
                 values=None, exclude=DEFAULT_EXCLUDE):
    """Charge balance the formula at a range of alkali amounts.

    Args:
        formula: formula string or {element: amount} dict.
        alkali: alkali metal to vary. If None, the single alkali metal present.
        interval, max_range: define the default grid (see alkali_values).
        values: explicit alkali amounts to use instead of the default grid.
        exclude: elements to leave out of the oxidation-state traces.
    """
    parsed = _parsed(formula)
    if alkali is None:
        alkali = _pick_alkali(parsed)
    if values is None:
        values = alkali_values(parsed.get(alkali, 0), interval, max_range)
    values = np.asarray(values, dtype=float)
    n = len(values)

    final = np.full(n, np.nan)
    states = {}
    for i, x in enumerate(values):
        try:
            r = charge_balance({**parsed, alkali: x})
        except Exception:
            r = None
        if r is None:
            continue
        final[i] = r.final_charge
        for s in r.oxidation_states:
            if s.element in exclude:
                continue
            states.setdefault((s.element, s.oxidation_state), np.zeros(n))[i] += s.quantity

    failed = np.isnan(final)
    for amounts in states.values():
        amounts[failed] = np.nan

    averages = {}
    for el in dict.fromkeys(el for el, _ in states):  # first-seen order
        own = {ox: q for (e, ox), q in states.items() if e == el}
        total = sum(own.values())
        with np.errstate(invalid="ignore", divide="ignore"):
            averages[el] = sum(ox * q for ox, q in own.items()) / total

    return SweepResult(parsed, alkali, values, final, states, averages)
