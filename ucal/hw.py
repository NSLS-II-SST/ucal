from sst_base.manipulator import Manipulator4AxBase, Manipulator1AxBase
from sst_base.motors import FlyableMotor, PrettyMotor
from sst_funcs.geometry.linalg import vec
from ophyd import Component as Cpt

# Note, multimesh is in sst_hw
manip_origin = vec(0, 0, 464, 0)


class Manipulator(Manipulator4AxBase):
    x = Cpt(FlyableMotor, "SampX}Mtr", name="x", kind='hinted')
    y = Cpt(FlyableMotor, "SampY}Mtr",  name="y", kind='hinted')
    z = Cpt(FlyableMotor, "SampZ}Mtr",  name="z", kind='hinted')
    r = Cpt(FlyableMotor, "SampTh}Mtr", name="r", kind='hinted')


def ManipulatorBuilder(prefix, *, name, **kwargs):
    return Manipulator(None, prefix, origin=manip_origin, name=name, **kwargs)


class MultiMesh(Manipulator1AxBase):
    x = Cpt(PrettyMotor, "MMesh}Mtr", name="Multimesh")


def MultiMeshBuilder(prefix, *, name, **kwargs):
    return MultiMesh(None, prefix, name=name, **kwargs)
