"""Safety-net tests: the refactor must not change any answers.

    pytest tests/

get_result() is the ONLY function that knows about the package's API.
When the API changes, update get_result() and nothing else. If the
tests still pass, the chemistry hasn't changed.
"""
import json
import math
from pathlib import Path

import pytest

from formulas import FORMULAS

SNAPSHOT = Path(__file__).parent / "snapshot.json"


def get_result(formula):
    """Return results in a fixed, API-independent shape:
    {"states": [[element, ox_state, quantity], ...] sorted,
     "final_charge": float, "is_balanced": bool, "string": str}
    or None if the formula can't be handled.
    """
    # ---- current API (update this block after the refactor) ----
    from approximate import charge_balance
    r = charge_balance(formula)
    if r is None:
        return None
    states = [[s.element, s.oxidation_state, s.quantity] for s in r.oxidation_states]
    d = {"final_charge": r.final_charge, "is_balanced": r.is_balanced}
    string = str(r)
    # -------------------------------------------------------------
    return {
        "states": sorted(states),
        "final_charge": d["final_charge"],
        "is_balanced": d["is_balanced"],
        "string": string,
    }


def _load():
    if not SNAPSHOT.exists():
        pytest.skip("No snapshot yet - run: python tests/make_snapshot.py")
    return json.loads(SNAPSHOT.read_text())


@pytest.mark.parametrize("formula", FORMULAS)
def test_matches_snapshot(formula):
    expected = _load()[formula]
    got = get_result(formula)

    if expected is None:
        assert got is None
        return
    assert got is not None

    assert len(got["states"]) == len(expected["states"])
    for (e1, ox1, q1), (e2, ox2, q2) in zip(got["states"], expected["states"]):
        assert (e1, ox1) == (e2, ox2)
        assert math.isclose(q1, q2, abs_tol=1e-9)

    assert math.isclose(got["final_charge"], expected["final_charge"], abs_tol=1e-9)
    assert got["is_balanced"] == expected["is_balanced"]
    assert got["string"] == expected["string"]