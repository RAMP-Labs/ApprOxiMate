"""Thin JSON bridge between the web UI and ApprOxiMate.

All chemistry happens in approx.approximate; this file only converts
results to JSON-friendly structures for the JavaScript front end.
"""
import json
import math

from approx.approximate import ApprOXimate

ALKALI_METALS = ["Li", "Na", "K", "Rb", "Cs"]
_analyzer = ApprOXimate()


def _clean(x):
    """Floats -> JSON-safe (NaN/inf become None)."""
    if x is None:
        return None
    x = float(x)
    return None if (math.isnan(x) or math.isinf(x)) else x


def _states(result):
    """Flatten ApprOxiMate's dict output to {element: [state, ...]}."""
    out = {}
    for element, data in result["elements"].items():
        states = data["states"] if "states" in data else [data]
        out[element] = [
            {
                "ox": int(s["oxidation_state"]),
                "qty": _clean(s["quantity"]),
                "fixed": bool(s.get("is_fixed", False)),
                "srp": _clean(s.get("srp")),
            }
            for s in states
        ]
    return out


def _balance(formula):
    formula = str(formula).strip()
    if not formula:
        return {"ok": False, "error": "Empty formula"}
    try:
        result = _analyzer.charge_balance(formula, return_format="dict")
    except Exception as e:  # keep the UI alive on bad input
        return {"ok": False, "error": f"Could not process formula: {e}"}
    if result is None or not result.get("elements"):
        return {"ok": False, "error": "Could not recognise any elements in this formula"}
    return {
        "ok": True,
        "elements": _states(result),
        "final": _clean(result["final_charge"]),
        "balanced": bool(result["is_balanced"]),
    }


def single(formula):
    return json.dumps(_balance(formula))


def batch(formulas_json):
    return json.dumps([_balance(f) for f in json.loads(formulas_json)])


def alkali_in(formula):
    """Alkali metals present in the formula, with their amounts."""
    try:
        parsed = _analyzer.parse_formula(str(formula).strip()) or {}
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
        parsed = _analyzer.parse_formula(str(formula).strip()) or {}
    except Exception as e:
        return json.dumps({"ok": False, "error": f"Could not parse formula: {e}"})
    amount = parsed.get(alkali, 0)
    if not amount or amount <= 0:
        return json.dumps({"ok": False, "error": f"{alkali} not found in formula"})

    n = max(1, int(n_intervals))
    xs, ys = [], []
    for k in range(n + 1):
        x = round(amount * k / n, 6)  # exact endpoints, no arange float drift
        try:
            r = _analyzer.charge_balance({**parsed, alkali: x}, return_format="dict")
            y = _clean(r["final_charge"]) if r else None
        except Exception:
            y = None
        xs.append(x)
        ys.append(y)
    return json.dumps({"ok": True, "x": xs, "y": ys, "amount": float(amount), "step": amount / n})
