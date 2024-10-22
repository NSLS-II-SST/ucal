from nbs_bl.sampleholders import Manipulator1AxBase
from nbs_bl.geometry.bars import Bar1d
from sst_base.motors import PrettyMotor
import numpy as np
from ophyd import Component as Cpt

# Need to somehow have a second-pass configuration, or linked configuration, or something
# refholder = SampleHolder(manipulator=multimesh, name="i0up_multimesh")
# geometry = make_1d_bar(160)

# refholder.add_geometry(geometry)

refsamples = [
    ("0", "C", (16, 20), 0),
    ("1", "HOPG", (26.2, 30.2), 0),
    ("2", "CaF2", (36.1, 40.1), 0),
    ("3", "TiN", (54.2, 58.2), 0),
    ("4", "V", (73.0, 77.0), 0),
    ("5", "Mn", (91.9, 95.9), 0),
    ("6", "CrFeCoNi", (110.9, 114.9), 0),
    ("7", "Blank", (131.5, 135.5), 0),
    ("8", "Photodiode", (149.0, 153.0), 0),
]

ref_dict = {
    "c": 0,
    "n": 3,
    "o": 6,
    "f": 2,
    "ca": 2,
    "ti": 3,
    "v": 4,
    "cr": 6,
    "mn": 5,
    "fe": 6,
    "co": 6,
    "ni": 6,
    "photodiode": 8,
    "empty": 7,
    "blank": 7,
    "zn": 7,
    "na": 7,
    "sr": 0,
    "hopg": 1,
}


def manipulatorFactory1Ax(xPV):
    class MultiMesh(Manipulator1AxBase):
        x = Cpt(PrettyMotor, xPV, name="Multimesh")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for s in refsamples:
                sid, name, coordinates, _ = s
                position = {"coordinates": [np.mean(coordinates)]}
                self.add_sample(name, sid, position)
            self.alias_dict = {
                "c": 0,
                "n": 3,
                "o": 6,
                "f": 2,
                "ca": 2,
                "ti": 3,
                "v": 4,
                "cr": 6,
                "mn": 5,
                "fe": 6,
                "co": 6,
                "ni": 6,
                "photodiode": 8,
                "empty": 7,
                "blank": 7,
                "zn": 7,
                "na": 7,
                "sr": 0,
                "hopg": 1,
            }

            self.set_sample("6")

        def set_sample(self, sample_id):
            if sample_id in self.samples:
                return super().set_sample(sample_id)
            else:
                sample_id = str(self.alias_dict.get(str(sample_id).lower(), "6"))
                return super().set_sample(sample_id)

    return MultiMesh


def MultiMeshBuilder(prefix, *, name, **kwargs):
    MultiMesh = manipulatorFactory1Ax("MMesh}Mtr")
    holder = Bar1d()
    return MultiMesh(prefix, origin=0, name=name, holder=holder, **kwargs)
