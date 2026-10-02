"""Run ONCE, before any refactoring, to record the current behaviour.

    python tests/make_snapshot.py

Writes tests/snapshot.json. Commit that file. Never regenerate it
unless you have deliberately changed the chemistry and checked the
new answers are right.
"""
import json
from pathlib import Path

from formulas import FORMULAS
from test_snapshot import get_result

out = {f: get_result(f) for f in FORMULAS}
path = Path(__file__).parent / "snapshot.json"
path.write_text(json.dumps(out, indent=2))
print(f"Saved {len(out)} results to {path}")