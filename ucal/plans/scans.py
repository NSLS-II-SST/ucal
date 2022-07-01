from .scan_base import wrap_xas, tes_gscan, xas_factory
from ucal.energy import en

"""
@wrap_xas("Zn")
def tes_zn_xas(**kwargs):
    yield from tes_gscan(en.energy, 1010, 1015, 0.5, 1030, 0.125, 1040, 0.2,
                         1060, 0.25, 1070, 0.5, **kwargs)
"""

_short_regions = {"Zn": [1010, 1015, 0.5, 1030, 0.125, 1040, 0.2, 1060, 0.25, 1070, 0.5],
            "Cu": [915, 920, 0.5, 926, 0.25, 934.5, 0.17, 947, 0.25, 954, 0.2, 970, 1],
            "Ni": [840, 845, 0.5, 848, 0.2, 858, 0.1, 867, 0.2, 874, 0.1, 882, 0.5, 900, 1],
            "Co": [765, 772, 0.5, 775, 0.2, 784, 0.1, 790, 0.2, 797, 0.1,
                   800, 0.2, 805, 0.5, 825, 1],
            "Fe": [697, 704, 0.5, 707, 0.2, 715, 0.1,
                   719, 0.5, 725, 0.1, 730, 0.5, 750, 1],
            "Mn": [630, 635, 0.5, 683, 0.2, 657, 0.1, 670, 0.5, 690, 1]
            }

#def extend_region(energy_region):
    
    
#_short_regions = 

tes_zn_xas = xas_factory([1010, 1015, 0.5, 1030, 0.125, 1040, 0.2,
                          1060, 0.25, 1070, 0.5], "Zn")

@wrap_xas("Cu")
def tes_cu_xas(**kwargs):
    yield from tes_gscan(en.energy, 915, 920, 0.5, 926, 0.25, 934.5, 0.17, 947,
                         0.25, 954, 0.2, 970, 1, **kwargs)


@wrap_xas("Ni")
def tes_ni_xas(**kwargs):
    yield from tes_gscan(en.energy, 840, 845, 0.5, 848, 0.2, 858, 0.1, 867,
                         0.2, 874, 0.1, 882, 0.5, 890, 1, **kwargs)


@wrap_xas("Co")
def tes_co_xas(**kwargs):
    yield from tes_gscan(en.energy, 755, 765, 1, 772, 0.5, 775, 0.2, 784, 0.1, 790,
                         0.2, 797, 0.1, 800, 0.2, 805, 0.5, 810, 1, 830, 2, **kwargs)


@wrap_xas("Fe")
def tes_fe_xas(**kwargs):
    yield from tes_gscan(en.energy, 690, 700, 1, 704, 0.5, 707, 0.2, 715, 0.1,
                         719, 0.5, 725, 0.1, 730, 0.5, 760, 1, **kwargs)


@wrap_xas("Mn")
def tes_mn_xas(**kwargs):
    yield from tes_gscan(en.energy, 630, 635, 0.5, 683, 0.2, 657, 0.1, 670,
                         0.5, **kwargs)


@wrap_xas("O")
def tes_o_xas(**kwargs):
    yield from tes_gscan(en.energy, 515, 520, 0.5, 526, 0.2, 535, 0.05, 545,
                         0.1, 555, 0.25, 585, 0.5, 600, 1, **kwargs)


@wrap_xas("N")
def tes_n_xas(**kwargs):
    yield from tes_gscan(en.energy, 380, 395, 0.5, 397, 0.1, 403, 0.05, 407, 0.1, 417, 0.2, 440, 0.5, 480, 2, **kwargs)


@wrap_xas("C")
def tes_c_xas(**kwargs):
    yield from tes_gscan(en.energy, 260, 263, 1, 278, 0.5, 282, 0.1, 287.5, 0.05, 290, 0.1, 300, 0.2, 310, 0.4, 320, 0.5, 350, 2, **kwargs)


@wrap_xas("C")
def tes_c_xas_long(**kwargs):
    yield from tes_gscan(en.energy, 250, 263, 1, 278, 0.5, 282, 0.1, 287.5, 0.05, 290, 0.1, 300, 0.2, 310, 0.4, 320, 0.5, 350, 2, **kwargs)


@wrap_xas("Fe")
def tes_fe_xas_short(**kwargs):
    yield from tes_gscan(en.energy, 700, 705, 1, 720, 0.5, 740, 1, **kwargs)
