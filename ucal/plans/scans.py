from .scan_base import xas_factory
from nbs_bl.queueserver import add_status
from nbs_bl.help import add_to_xas_list
from nbs_bl.globalVars import GLOBAL_XAS_PLANS


_default_regions = {"Na": [1055, 1065, 1, 1070, 0.2, 1080, 0.1, 1100, 0.2, 1140, 1.0],
                    "Zn": [1010, 1015, 0.5, 1030, 0.125, 1040, 0.2, 1060,
                           0.25, 1080, 1.0],
                    "Cu": [915, 920, 0.5, 926, 0.25, 934.5, 0.17, 947,
                           0.25, 954, 0.2, 960, 0.5, 980, 1],
                    "Ce": [855, 865, 1, 870, 0.5, 875, 0.2, 885, 0.1, 891,
                           0.2, 901, 0.1, 905, 0.2, 910, 0.5, 935, 1],
                    "Ni": [830, 840, 1, 845, 0.5, 848, 0.2, 858, 0.1, 867, 0.2,
                           874, 0.1, 882, 0.5, 900, 1],
                    "Co": [755, 765, 1, 772, 0.5, 775, 0.2, 784, 0.1, 790,
                           0.2, 797, 0.1, 800, 0.2, 805, 0.5, 810, 1, 830, 2],
                    "Fe": [690, 700, 1, 704, 0.5, 707, 0.2, 715, 0.1,
                           719, 0.5, 725, 0.1, 730, 0.5, 760, 1],
                    "Mn": [625, 635, 0.5, 638, 0.2, 645, 0.1, 650, 0.2, 655, 0.1, 670, 0.5, 690, 1],
                    "O": [515, 520, 0.5, 526, 0.2, 535, 0.05, 545,
                          0.1, 555, 0.25, 585, 0.5, 600, 1],
                    "Ti": [430, 450, 1, 470, 0.1, 480, 0.2, 500, 0.5, 510, 1],
                    "N": [380, 395, 0.5, 397, 0.1, 403, 0.05, 407, 0.1, 417,
                          0.2, 440, 0.5, 480, 2],
                    "C": [260, 263, 1, 284, 0.5, 292,
                          0.1, 300, 0.2, 310, 0.4, 320, 0.5, 350, 2],
                    "Sr": [245, 255, 1, 260, 0.5, 265, 0.2, 290, 0.1, 300, 0.2, 310, 0.4, 320, 1]}

_short_regions = {"C": [270, 278, 0.5, 282, 0.1, 287.5, 0.05, 290,
                        0.1, 300, 0.2, 310, 0.4, 320, 0.5],
                  "O": [515, 520, 0.5, 526, 0.2, 535, 0.05, 545,
                        0.1, 555, 0.5]}

#def extend_region(energy_region):
# Time info:
# C:
# N:
# O: 10
# Fe:
# Co:
# Ni:
# Ce: 7:30
# Cu: 4:30
# Zn: 6:30


for e, region in _default_regions.items():
    name = f"{e.lower()}_xas"
    add_to_xas_list(xas_factory(region, e, name))
    GLOBAL_XAS_PLANS[e] = name

add_status("XAS_PLANS", GLOBAL_XAS_PLANS)

for e, region in _short_regions.items():
    name = f"{e.lower()}_short_xas"
    add_to_xas_list(xas_factory(region, e, name))

c_ru_xas = xas_factory([260, 263, 1, 282, 0.5, 292, 0.1, 300, 0.2, 310, 0.4, 320, 0.5, 350, 2], 'C', 'c_ru_xas')
