"""Thin JSON bridge between the web UI and ApprOxiMate.

All chemistry happens in approximate.core; this file only converts
results to JSON-friendly structures for the JavaScript front end.
"""
import json
import math

from approximate.capacity import ALKALI_METALS, capacity as _capacity
from approximate.core import charge_balance, parse_formula


def _clean(x):
    """Floats -> JSON-safe (NaN/inf become None)."""
    if x is None:
        return None
    x = float(x)
    return None if (math.isnan(x) or math.isinf(x)) else x


def _states(result):
    """Group a BalanceResult's oxidation states as {element: [state, ...]}."""
    out = {}
    for s in result.oxidation_states:
        out.setdefault(s.element, []).append({
            "ox": int(s.oxidation_state),
            "qty": _clean(s.quantity),
            "fixed": bool(s.is_fixed),
            "srp": _clean(s.srp),
        })
    return out


def _balance(formula):
    formula = str(formula).strip()
    if not formula:
        return {"ok": False, "error": "Empty formula"}
    try:
        result = charge_balance(formula)
    except Exception as e:  # keep the UI alive on bad input
        return {"ok": False, "error": f"Could not process formula: {e}"}
    if result is None or not result.oxidation_states:
        return {"ok": False, "error": "Could not recognise any elements in this formula"}
    return {
        "ok": True,
        "elements": _states(result),
        "final": _clean(result.final_charge),
        "balanced": bool(result.is_balanced),
    }


def single(formula):
    return json.dumps(_balance(formula))


def batch(formulas_json):
    return json.dumps([_balance(f) for f in json.loads(formulas_json)])


def alkali_in(formula):
    """Alkali metals present in the formula, with their amounts."""
    try:
        parsed = parse_formula(str(formula).strip()) or {}
    except Exception:
        parsed = {}
    return json.dumps(
        [{"el": el, "amount": float(parsed[el])} for el in ALKALI_METALS if parsed.get(el, 0) > 0]
    )


def sweep(formula, alkali, n_intervals):
    """Charge balance as the alkali amount goes from 0 to its value in the formula.

    The x-range always follows the formula (e.g. Na0.67... -> 0 to 0.67),
    split into n_intervals equal steps (n_intervals + 1 points, both ends included).
    """
    try:
        parsed = parse_formula(str(formula).strip()) or {}
    except Exception as e:
        return json.dumps({"ok": False, "error": f"Could not parse formula: {e}"})
    amount = parsed.get(alkali, 0)
    if not amount or amount <= 0:
        return json.dumps({"ok": False, "error": f"{alkali} not found in formula"})

    n = max(1, int(n_intervals))
    skip = set(ALKALI_METALS) | {"O"}
    xs, ys, rows = [], [], []
    for k in range(n + 1):
        x = round(amount * k / n, 6)  # exact endpoints, no arange float drift
        try:
            r = charge_balance({**parsed, alkali: x})
        except Exception:
            r = None
        xs.append(x)
        ys.append(_clean(r.final_charge) if r else None)
        # Variable oxidation states only (alkali metals, O and fixed states excluded)
        row = None
        if r:
            row = {}
            for el, states in _states(r).items():
                if el in skip:
                    continue
                for st in states:
                    if not st["fixed"]:
                        key = (el, st["ox"])
                        row[key] = row.get(key, 0.0) + (st["qty"] or 0.0)
        rows.append(row)

    # One series per (element, oxidation state) seen anywhere in the sweep.
    # A state absent at a given x is 0 there; a failed calculation is None.
    keys = sorted({key for row in rows if row for key in row})
    states = [
        {"el": el, "ox": ox, "y": [None if row is None else row.get((el, ox), 0.0) for row in rows]}
        for el, ox in keys
    ]
    return json.dumps({"ok": True, "x": xs, "y": ys, "states": states,
                       "amount": float(amount), "step": amount / n})


def capacity(formula, alkali, interval=0.01, tol=1e-6):
    """Theoretical vs charge-balance-adjusted capacity (mAh/g).

    See approximate.capacity.capacity for the method.
    """
    try:
        c = _capacity(formula, alkali, interval=interval, tol=tol)
    except ValueError as e:
        return json.dumps({"ok": False, "error": str(e)})
    except Exception as e:
        return json.dumps({"ok": False, "error": f"Could not process formula: {e}"})
    return json.dumps({
        "ok": True,
        "full": c.full,
        "removable": round(c.removable, 6),
        "remaining_at_limit": round(c.remaining, 6),
        "molar_mass": c.molar_mass,
        "per_unit": c.per_alkali,
        "q_max": c.q_theoretical,
        "q_adj": c.q_adjusted,
    })
