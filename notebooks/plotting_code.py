"""House style and figure helpers for the ApprOxiMate paper notebooks.

The chemistry plots now live in the package:  from approximate.plotting import ...
"""
import warnings

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.gridspec import GridSpec

# First installed font wins: Aptos + Helvetica on Windows, Carlito + Nimbus Sans on Linux.
TEXT_FONTS = ["Aptos", "Carlito"]
MATH_FONTS = ["Nimbus Sans", "Helvetica"]


def _register_system_fonts(names):
    """Make sure matplotlib knows about system copies of these fonts."""
    for path in fm.findSystemFonts():
        if any(name.replace(" ", "").lower() in path.replace(" ", "").lower() for name in names):
            try:
                fm.fontManager.addfont(path)
            except Exception:
                pass


def _first_available(names):
    for name in names:
        try:
            fm.findfont(fm.FontProperties(family=name), fallback_to_default=False)
            return name
        except ValueError:
            continue
    return names[0]  # none installed: matplotlib falls back with a warning


def apply_style(os_choice=None):
    """Apply the paper figure style.

    Fonts are picked automatically from TEXT_FONTS / MATH_FONTS, so the same
    call works on Windows and Linux. `os_choice` is accepted for old notebooks
    but no longer needed.
    """
    if os_choice is not None:
        warnings.warn("apply_style() picks fonts automatically; os_choice is ignored.",
                      DeprecationWarning, stacklevel=2)

    _register_system_fonts(TEXT_FONTS + MATH_FONTS)
    base_font = _first_available(TEXT_FONTS)
    math_font = _first_available(MATH_FONTS)

    plt.rcParams.update({
        'font.size': 14,
        'axes.labelsize': 14,
        'axes.titlesize': 16,
        'xtick.labelsize': 14,
        'ytick.labelsize': 14,
        'legend.fontsize': 12,
        'font.family': [base_font],
        'mathtext.fontset': 'custom',
        'mathtext.rm': base_font,
        'mathtext.it': f'{math_font}:italic',
        'mathtext.bf': f'{math_font}:bold',
        'mathtext.cal': f'{math_font}:italic',
        'mathtext.sf': base_font,
        'mathtext.tt': 'DejaVu Sans Mono',
        'lines.linewidth': 1.5,
        'lines.markersize': 4,
        'axes.linewidth': 1.5,
        'xtick.direction': 'in',
        'ytick.direction': 'in',
        'xtick.top': True,
        'ytick.right': True,
        'xtick.minor.visible': True,
        'ytick.minor.visible': True,
        'xtick.major.width': 1,
        'ytick.major.width': 1,
        'xtick.minor.width': 0.5,
        'ytick.minor.width': 0.5,
        'xtick.major.size': 4,
        'ytick.major.size': 4,
        'xtick.minor.size': 1.5,
        'ytick.minor.size': 1.5,
        'legend.frameon': False,
        'legend.handlelength': 2,
        'legend.handletextpad': 0.5,
        'figure.dpi': 100,
        'savefig.dpi': 600,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.02,
    })
    return base_font, math_font


def add_panel_label(ax, label, x=0.05, y=0.95, fontsize=16, fontweight='bold'):
    """Add a panel label such as '(a)' to the top-left inside corner of an axis."""
    ax.text(x, y, label, transform=ax.transAxes,
            fontsize=fontsize, fontweight=fontweight, va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                      edgecolor='none', alpha=0.8))


def create_multi_panel_figure(nrows=1, ncols=2, figsize=None,
                              width_ratios=None, height_ratios=None,
                              hspace=0.3, wspace=0.3):
    """Create a figure with a GridSpec of panels.

    Returns (fig, axes), with axes squeezed like plt.subplots
    (single Axes, 1-D array, or 2-D array).
    """
    if figsize is None:
        figsize = (6 * ncols, 5 * nrows)

    fig = plt.figure(figsize=figsize)
    gs = GridSpec(nrows, ncols, figure=fig,
                  width_ratios=width_ratios, height_ratios=height_ratios,
                  hspace=hspace, wspace=wspace)

    axes = np.array([[fig.add_subplot(gs[i, j]) for j in range(ncols)]
                     for i in range(nrows)])

    if nrows == 1 and ncols == 1:
        return fig, axes[0, 0]
    elif nrows == 1:
        return fig, axes[0]
    elif ncols == 1:
        return fig, axes[:, 0]
    return fig, axes