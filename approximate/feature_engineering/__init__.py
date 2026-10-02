"""Oxidation-state-aware feature engineering.

Needs the optional dependencies:  pip install "approximate[features]"
"""
try:
    import mendeleev  # noqa: F401
    import pymatgen.core  # noqa: F401
except ImportError as e:  # pragma: no cover
    raise ImportError(
        'approximate.feature_engineering needs mendeleev and pymatgen: '
        'pip install "approximate[features]"'
    ) from e

from .valence_features import ValenceFeatureModule
from .feature_extractor import MaterialFeatureExtractor
from .element_property_features import ElementPropertyModule
from .ionic_radius_features import IonicRadiusModule
from .layered_ox_features import TransitionMetalPotentialModule
from .magnetic_moment_features import MagneticMomentModule
from .electronegativity_features import ElectronegativityModule
from .stats_expander import StatsExpander