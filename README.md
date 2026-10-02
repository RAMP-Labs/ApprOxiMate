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

## Citation
Please cite this package.

## Try it in your browser

**No installation needed:** [ramp-labs.github.io/ApprOxiMate](https://ramp-labs.github.io/ApprOxiMate/)

If you just want answers rather than code, the web calculator does it all in your browser:

| Tab | What it does |
|---|---|
| **Single composition** | Type a formula like `Na0.67Ni0.33Mn0.67O2` and get the oxidation state of every element |
| **Batch from file** | Upload a CSV or Excel file of formulas and download the results |
| **Charge balance plot** | See how charge balance changes as alkali is removed |
| **Capacity** | Theoretical vs charge-balance-adjusted capacity (mAh/g) |

Everything runs locally in your browser using [Pyodide](https://pyodide.org), so your compositions never leave your computer.


## Installation

```bash
pip install approximate
```
[PyPI/approximate](https://pypi.org/project/approximate/)

For development, clone the repository and install it in editable mode:

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
from approximate import charge_balance

r = charge_balance("Fe3O4")
print(r)                # O:-2:4.0;Fe:2:1.0;Fe:3:2.0;FinalChargeBalance:0.0
r.oxidation_states      # one entry per (element, oxidation state)
r.final_charge          # 0.0
r.is_balanced           # True
r.to_dataframe()        # oxidation states as a table
r.to_dict()             # everything as a dictionary
```

Shortcuts when you only need one thing:

```python
from approximate import oxidation_states, final_charge, parse_formula

oxidation_states("LiFePO4")                     # list of states
oxidation_states("LiFePO4", as_dataframe=True)  # as a DataFrame
final_charge("NaMn0.5Ni0.5O2")                  # 0.0
parse_formula("LiFePO4")                        # {'Li': 1.0, 'Fe': 1.0, 'P': 1.0, 'O': 4.0}
```

Every function accepts `verbose=True` (step-by-step log) and `precision=`.

## Feature Engineering

Use `MaterialFeatureExtractor` to generate oxidation-state-aware features for
one formula or many formulae:

```python
import pandas as pd
from approximate.feature_engineering import MaterialFeatureExtractor

# The periodic table is loaded from mendeleev automatically.
# Pass your own as the first argument to reuse or customise it.
extractor = MaterialFeatureExtractor(mode="both", ionic_radius_unit="pm")

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
approximate/
  core.py                     # Charge-balancing engine and public functions
  Data/                       # Oxidation-state and SRP lookup data
  feature_engineering/        # Descriptor modules and feature extractor
notebooks/                    # Experiments, datasets, outputs, and analysis
site/                         # Web calculator (GitHub Pages, runs in-browser via Pyodide)
tutorial_notebook.ipynb       # Introductory usage notebook
```

## Standard Reduction Potential Data
NIST dataset was used to collected SRP values used within the variable_ox_states_srps.csv 

S. G. Bratsch, Standard Electrode Potentials and Temperature Coefficients in Water at 298.15 K, Journal of Physical and Chemical Reference Data, 1989, 18, 1–21.

### Data Cleanup Note
An earlier version of Parsed_Data.csv contained 2,302 raw entries. The current Parsed_Data.csv now has 2,299 raw entries as 3 formula were lost when transferred over to ICSD_CrystStrucData.csv. This 2,299 dataset was then preprocessed and cleaned resulting in a dataset of 2,283 entires as seen in `notebooks/exp1_featurisation.ipynb` these 16 formulas were removed due to numerical precision limits encountered when parsing and balancing large formula units and therfore were unable to be charge balanced successfully. 

## License

This project is licensed under the MIT License. See `LICENSE` for details.
