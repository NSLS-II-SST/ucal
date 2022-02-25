from .scan_base import wrap_xas, tes_gscan
from ucal_hw.energy import en


@wrap_xas("Zn")
def tes_zn_xas(**kwargs):
    yield from tes_gscan(en.energy, 1010, 1015, 0.5, 1030, 0.125, 1040, 0.2,
                         1060, 0.25, 1070, 0.5, **kwargs)


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
    yield from tes_gscan(en.energy, 765, 772, 0.4, 775, 0.2, 784, 0.1, 790,
                         0.2, 797, 0.1, 800, 0.2, 805, 0.4, 810, 1, **kwargs)


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


@wrap_xas("Fe")
def tes_fe_xas_short(**kwargs):
    yield from tes_gscan(en.energy, 700, 705, 1, 720, 0.5, 740, 1, **kwargs)


@wrap_xas("C")
def tes_c_xas(**kwargs):
    yield from tes_gscan(en.energy, 270, 280, 1, 300, 0.1, 310, 0.2, 350, 1,
                         **kwargs)
