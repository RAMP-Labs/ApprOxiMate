"""ApprOxiMate: composition-only mixed oxidation state estimation.

    from approximate import charge_balance
    r = charge_balance("Fe3O4")
"""
from .core import (
    BalanceResult,
    ElementState,
    charge_balance,
    final_charge,
    oxidation_states,
    parse_formula,
)

__version__ = "0.1.0"

__all__ = [
    "charge_balance",
    "oxidation_states",
    "final_charge",
    "parse_formula",
    "BalanceResult",
    "ElementState",
]
