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
    skip = set(ALKALI_METALS) | {"O"}
    xs, ys, rows = [], [], []
    for k in range(n + 1):
        x = round(amount * k / n, 6)  # exact endpoints, no arange float drift
        try:
            r = _analyzer.charge_balance({**parsed, alkali: x}, return_format="dict")
        except Exception:
            r = None
        xs.append(x)
        ys.append(_clean(r["final_charge"]) if r else None)
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


# Standard atomic weights (g/mol), taken from mendeleev so results match the notebooks.
ATOMIC_MASS = {
    "H": 1.008, "He": 4.002602, "Li": 6.94, "Be": 9.0121831, "B": 10.81, "C": 12.011,
    "N": 14.007, "O": 15.999, "F": 18.998403163, "Ne": 20.1797, "Na": 22.98976928,
    "Mg": 24.305, "Al": 26.9815385, "Si": 28.085, "P": 30.973761998, "S": 32.06, "Cl": 35.45,
    "Ar": 39.948, "K": 39.0983, "Ca": 40.078, "Sc": 44.955908, "Ti": 47.867, "V": 50.9415,
    "Cr": 51.9961, "Mn": 54.938044, "Fe": 55.845, "Co": 58.933194, "Ni": 58.6934,
    "Cu": 63.546, "Zn": 65.38, "Ga": 69.723, "Ge": 72.63, "As": 74.921595, "Se": 78.971,
    "Br": 79.904, "Kr": 83.798, "Rb": 85.4678, "Sr": 87.62, "Y": 88.90584, "Zr": 91.224,
    "Nb": 92.90637, "Mo": 95.95, "Tc": 97.90721, "Ru": 101.07, "Rh": 102.9055, "Pd": 106.42,
    "Ag": 107.8682, "Cd": 112.414, "In": 114.818, "Sn": 118.71, "Sb": 121.76, "Te": 127.6,
    "I": 126.90447, "Xe": 131.293, "Cs": 132.90545196, "Ba": 137.327, "La": 138.90547,
    "Ce": 140.116, "Pr": 140.90766, "Nd": 144.242, "Pm": 144.91276, "Sm": 150.36,
    "Eu": 151.964, "Gd": 157.25, "Tb": 158.92535, "Dy": 162.5, "Ho": 164.93033,
    "Er": 167.259, "Tm": 168.93422, "Yb": 173.045, "Lu": 174.9668, "Hf": 178.49,
    "Ta": 180.94788, "W": 183.84, "Re": 186.207, "Os": 190.23, "Ir": 192.217, "Pt": 195.084,
    "Au": 196.966569, "Hg": 200.592, "Tl": 204.38, "Pb": 207.2, "Bi": 208.9804, "Po": 209.0,
    "At": 210.0, "Rn": 222.0, "Fr": 223.0, "Ra": 226.0, "Ac": 227.0, "Th": 232.0377,
    "Pa": 231.03588, "U": 238.02891, "Np": 237.0, "Pu": 244.0, "Am": 243.0, "Cm": 247.0,
    "Bk": 247.0, "Cf": 251.0, "Es": 252.0, "Fm": 257.0, "Md": 258.0, "No": 259.0,
    "Lr": 262.0, "Rf": 267.0, "Db": 268.0, "Sg": 271.0, "Bh": 274.0, "Hs": 269.0,
    "Mt": 276.0, "Ds": 281.0, "Rg": 281.0, "Cn": 285.0, "Nh": 286.0, "Fl": 289.0,
    "Mc": 288.0, "Lv": 293.0, "Ts": 294.0, "Og": 294.0,
}

FARADAY = 96485  # C/mol, as in parity_plot_theo_cap.ipynb


def _molar_mass(parsed):
    missing = [el for el in parsed if el not in ATOMIC_MASS]
    if missing:
        raise ValueError(f"No atomic mass for {', '.join(missing)}")
    return sum(ATOMIC_MASS[el] * q for el, q in parsed.items())


def capacity(formula, alkali, interval=0.01, tol=1e-6):
    """Theoretical vs charge-balance-adjusted capacity (mAh/g).

    Same method as find_max_na_removed in parity_plot_theo_cap.ipynb:
    step the alkali amount down from its full value in fixed `interval` steps
    and stop at the first composition that is no longer charge neutral.
      Q_max = x_full * F / (3.6 * M)
      Q_adj = x_removable * F / (3.6 * M)
    M is the molar mass of the starting (fully alkali-loaded) formula.
    """
    try:
        parsed = _analyzer.parse_formula(str(formula).strip()) or {}
    except Exception as e:
        return json.dumps({"ok": False, "error": f"Could not parse formula: {e}"})
    full = parsed.get(alkali, 0)
    if not full or full <= 0:
        return json.dumps({"ok": False, "error": f"{alkali} not found in formula"})
    try:
        mass = _molar_mass(parsed)
    except ValueError as e:
        return json.dumps({"ok": False, "error": str(e)})

    n_steps = max(1, int(round(full / interval)))
    last_ok = full
    for k in range(n_steps + 1):
        remaining = full * (1 - k / n_steps)  # includes 0 exactly, like np.linspace
        try:
            r = _analyzer.charge_balance({**parsed, alkali: remaining}, return_format="object")
            charge = r.final_charge if r else float("nan")
        except Exception:
            charge = float("nan")
        if math.isnan(charge) or abs(charge) > tol:
            break
        last_ok = remaining

    per_unit = FARADAY / (3.6 * mass)  # mAh/g per formula unit of alkali removed
    removable = full - last_ok
    return json.dumps({
        "ok": True,
        "full": float(full),
        "removable": round(removable, 6),
        "remaining_at_limit": round(last_ok, 6),
        "molar_mass": mass,
        "per_unit": per_unit,
        "q_max": full * per_unit,
        "q_adj": removable * per_unit,
    })
