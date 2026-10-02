"""Formulas used by the snapshot tests.

Add any formula you care about here. The point is coverage of every
kind of case the code handles, not just the happy path.
"""

FORMULAS = [
    # simple, single oxidation state
    "NaCl", "LiFePO4", "LiCoO2", "KMnO4", "Li2MnO3",
    # mixed valence (split states)
    "Fe3O4", "Na0.67Ni0.33Mn0.67O2",
    # cathode-style compositions
    "NaMn0.5Ni0.5O2", "NaNi1/3Fe1/3Mn1/3O2", "Na2/3Mn2/3Ni1/3O2",
    # alloys
    "CuZn", "Fe0.5Ni0.5",
    # can't fully balance
    "Na3O",
    # edge cases
    "",          # empty
    "Xx2O",      # unknown element -> currently returns None
    "Ca(OH)2",   # brackets -> currently parsed incorrectly (see notes)
]