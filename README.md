# ApprOxiMate

ApprOxiMate is a Python package for charge balancing inorganic chemical
formulae and generating oxidation-state-aware descriptors for materials
informatics workflows.

The project combines a charge-balancing routine with feature engineering
modules for valence structure, elemental properties, ionic radii,
electronegativity, magnetic moments, and related composition statistics.
It is designed for use in notebooks and machine-learning pipelines where
oxidation states provide useful chemical context beyond formula-only
descriptors.

## Features

- Charge balance inorganic formulae using fixed and variable oxidation-state
  data.
- Return balanced results as strings, dictionaries, pandas DataFrames, or
  structured Python objects.
- Generate descriptors for all elements in a composition and for variable
  oxidation-state elements separately.
- Build feature matrices from lists of formulae for downstream modelling.
- Includes example notebooks for featurisation, exploratory analysis, model
  training, and result assessment.

## Standard Reduction Potential Data
NIST dataset was used to collected SRP values used within the variable_ox_states_srps.csv 

S. G. Bratsch, Standard Electrode Potentials and Temperature Coefficients in Water at 298.15 K, Journal of Physical and Chemical Reference Data, 1989, 18, 1–21.

## Citation
Please cite this package.

## Installation

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/RAMP-Labs/ApprOxiMate.git
cd ApprOxiMate
python -m pip install -e .
```

For notebook and development dependencies:

```bash
python -m pip install -e ".[dev]"
```

ApprOxiMate requires Python 3.10 or newer.

## Quick Start

```python
from approx.approximate import ApprOXimate

approx = ApprOXimate()

result = approx.charge_balance("LiFePO4", return_format="string")
print(result)
```

Example output:

```text
Li:1:1.0;O:-2:4.0;Fe:2:1.0;P:5:1.0;FinalChargeBalance:0.0
```

The same result can be returned in different formats:

```python
as_dict = approx.charge_balance("LiFePO4", return_format="dict")
as_dataframe = approx.charge_balance("LiFePO4", return_format="dataframe")
as_object = approx.charge_balance("LiFePO4", return_format="object")
```

## Feature Engineering

Use `MaterialFeatureExtractor` to generate oxidation-state-aware features for
one formula or many formulae:

```python
import pandas as pd
from mendeleev.fetch import fetch_table

from approx.approximate import ApprOXimate
from approx.feature_engineering import MaterialFeatureExtractor

approx = ApprOXimate()
ptable = fetch_table("elements")

extractor = MaterialFeatureExtractor(
    approx,
    ptable,
    mode="both",
    ionic_radius_unit="pm",
)

features = extractor.get_features("LiFePO4")
feature_table = pd.DataFrame(
    extractor.featurize_many(["LiFePO4", "NaCoO2"])
)
```

`mode` controls which feature groups are returned:

- `"all"`: descriptors calculated over all elements in the formula.
- `"var"`: descriptors calculated only over variable oxidation-state elements.
- `"both"`: include both groups.

The available feature modules include:

- `ValenceFeatureModule`
- `ElementPropertyModule`
- `IonicRadiusModule`
- `MagneticMomentModule`
- `ElectronegativityModule`
- `TransitionMetalPotentialModule`

The transition-metal potential module is optional and can be enabled with:

```python
extractor = MaterialFeatureExtractor(
    approx,
    ptable,
    enable_tm_potential=True,
    tm_cation="Na",
    tm_anion="O",
)
```

## Notebooks

The repository includes notebooks that demonstrate the main workflow:

- `tutorial_notebook.ipynb`: introductory charge-balancing examples.
- `notebooks/exp1_featurisation.ipynb`: dataset featurisation.
- `notebooks/exp2_EDA_of_dataset.ipynb`: exploratory data analysis.
- `notebooks/exp3a_approx_runML.ipynb`: modelling with ApprOxiMate features.
- `notebooks/exp3b_magpie_runML.ipynb`: comparison modelling with Magpie-style features.
- `notebooks/exp3c_oliynyk_runML.ipynb`: comparison modelling with Oliynyk-style features.
- `notebooks/exp4_assessing_models.ipynb`: model assessment and visualisation.

Notebooks with `exp0_` in the front show multiple ways to use ApprOxiMate outside of feature engineering and machine learning. Such as:

- `alkali_removal_notebook.ipynb`: Charge balance plots and theoretical oxidation state tracking.
- `parity_plot_theo_cap.ipynb`: Adjust theoretical capacity calculations using ApprOxiMates charge balance assessment. 
- `srp_analysis.ipynb`: Since the user is able to change the SRP data to what fits their needs, this notebook helps visualise this.

## Project Layout

```text
approx/
  approximate.py              # Charge-balancing engine
  Data/                       # Oxidation-state and SRP lookup data
  feature_engineering/        # Descriptor modules and feature extractor
notebooks/                    # Experiments, datasets, outputs, and analysis
website_widget/               # Interactive notebook widget prototype
tutorial_notebook.ipynb       # Introductory usage notebook
```

## License

This project is licensed under the MIT License. See `LICENSE` for details.
