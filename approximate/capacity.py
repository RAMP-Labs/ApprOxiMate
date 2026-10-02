"""Theoretical and charge-balance-adjusted capacity.

Pure Python (only depends on approximate.core), so it also runs in the
browser via Pyodide for the ApprOxiMate website.

    >>> from approximate import capacity
    >>> c = capacity("NaFe0.5Co0.5O2")
    >>> round(c.q_theoretical, 1), round(c.q_adjusted, 1)
    (238.5, 119.2)

Assumptions:
    * one electron transferred per alkali ion removed;
    * molar mass is that of the starting (fully alkali-loaded) formula.
"""
from dataclasses import asdict, dataclass

from .core import charge_balance, parse_formula

#: Faraday constant in C/mol (exact, 2019 SI redefinition).
FARADAY = 96485.33212

ALKALI_METALS = ("Li", "Na", "K", "Rb", "Cs")

# Standard atomic weights (g/mol): IUPAC/CIAAW 2013 values with the 2015
# ytterbium revision, as distributed by the mendeleev package.
#   J. Meija et al., "Atomic weights of the elements 2013 (IUPAC Technical
#   Report)", Pure Appl. Chem. 88, 265-291 (2016). doi:10.1515/pac-2015-0305
#   CIAAW, "Standard atomic weight of ytterbium revised", Chem. Int. 37(5-6),
#   26 (2015). doi:10.1515/ci-2015-0512
# Values are kept identical to mendeleev (checked in tests/test_capacity.py) so
# that capacities agree with the feature engineering, which uses mendeleev.
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


@dataclass(frozen=True)
class CapacityResult:
    """Result of capacity().

    Attributes:
        alkali: the alkali metal being removed.
        full: alkali per formula unit in the starting formula.
        removable: alkali that can be removed before the formula can no
            longer be charge balanced.
        remaining: alkali left at that limit (full - removable).
        molar_mass: molar mass of the starting formula, g/mol.
        q_theoretical: capacity if all alkali is removed, mAh/g.
        q_adjusted: capacity limited by charge balance, mAh/g.
    """
    alkali: str
    full: float
    removable: float
    remaining: float
    molar_mass: float
    q_theoretical: float
    q_adjusted: float

    @property
    def per_alkali(self) -> float:
        """mAh/g per formula unit of alkali removed."""
        return self.q_theoretical / self.full

    def to_dict(self) -> dict:
        return asdict(self)


def _as_parsed(formula):
    if isinstance(formula, dict):
        return dict(formula)
    parsed = parse_formula(str(formula).strip())
    if not parsed:
        raise ValueError(f"Could not parse formula {formula!r} (unknown element?)")
    return parsed


def molar_mass(formula) -> float:
    """Molar mass in g/mol of a formula string or {element: amount} dict."""
    parsed = _as_parsed(formula)
    missing = [el for el in parsed if el not in ATOMIC_MASS]
    if missing:
        raise ValueError(f"No atomic mass for {', '.join(missing)}")
    return sum(ATOMIC_MASS[el] * q for el, q in parsed.items())


def _pick_alkali(parsed):
    present = [el for el in ALKALI_METALS if parsed.get(el, 0) > 0]
    if len(present) != 1:
        found = ", ".join(present) if present else "none"
        raise ValueError(f"Specify alkali= (alkali metals found: {found})")
    return present[0]


def capacity(formula, alkali=None, interval=0.01, tol=1e-6, faraday=FARADAY):
    """Theoretical vs charge-balance-adjusted capacity (mAh/g).

    Steps the alkali amount down from its full value in `interval` steps and
    stops at the first composition that is no longer charge neutral
    (|final charge| > tol). The last neutral composition sets how much
    alkali is removable.

        Q_theoretical = full      * F / (3.6 * M)
        Q_adjusted    = removable * F / (3.6 * M)

    Args:
        formula: formula string or {element: amount} dict.
        alkali: alkali metal to remove. If None, the single alkali metal
            in the formula is used.
        interval: step size in alkali per formula unit (paper: 0.01).
        tol: charge tolerance for "still balanced".
        faraday: Faraday constant, C/mol.

    Raises:
        ValueError: unparsable formula, unknown element, or alkali not present.
    """
    parsed = _as_parsed(formula)
    if alkali is None:
        alkali = _pick_alkali(parsed)
    full = parsed.get(alkali, 0)
    if not full or full <= 0:
        raise ValueError(f"{alkali} not found in formula")
    mass = molar_mass(parsed)

    n_steps = max(1, int(round(full / interval)))
    step = -full / n_steps
    last_ok = full
    for k in range(n_steps + 1):
        # same values as np.linspace(full, 0, n_steps + 1), endpoint exactly 0
        remaining = 0.0 if k == n_steps else full + k * step
        try:
            r = charge_balance({**parsed, alkali: remaining})
            charge = r.final_charge if r is not None else float("nan")
        except Exception:
            charge = float("nan")
        if charge != charge or abs(charge) > tol:  # NaN or unbalanced
            break
        last_ok = remaining

    per_unit = faraday / (3.6 * mass)
    removable = full - last_ok
    return CapacityResult(
        alkali=alkali,
        full=float(full),
        removable=removable,
        remaining=last_ok,
        molar_mass=mass,
        q_theoretical=full * per_unit,
        q_adjusted=removable * per_unit,
    )
