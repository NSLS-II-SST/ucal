import asyncio
from bluesky.run_engine import RunEngine, TransitionError
import numpy as np
import os
import pytest
from bl_funcs.geometry.linalg import vec, deg_to_rad, rotz
from bl_base.sampleholder import make_regular_polygon
import ucal_common
ucal_common.STATION_NAME = "sst_sim"
from ucal_common.motors import (manipx, manipy, manipz, manipr,
                                manipulator)
from ucal_common.sampleholder import sampleholder
from ucal_common.run_engine import setup_run_engine


@pytest.fixture()
def fresh_manipulator():
    h = 100
    w = 10
    # points = [vec(w/2, w/2, 0), vec(w/2, w/2, 1), vec(w/2, -w/2, 0)]
    geometry = make_regular_polygon(w, h, 4)
    sampleholder.add_geometry(geometry)
    sampleholder.set("side1")
    x, y, _ = manipulator.origin
    z = manipulator.forward(0, 0, 0, 0).z
    manipx.set(x)
    manipy.set(y)
    # Sink manipz so that we are blocking beam
    manipz.set(z + 1)
    manipr.set(0)
    yield manipulator
    sampleholder._reset()


@pytest.fixture(params=[4, 5, 6])
def random_angle_manipulator(request):
    angle = 5*np.random.rand()
    w = request.param
    h = 100
    theta = deg_to_rad(angle)
    p1 = vec(w, w, 100)
    p2 = p1 + vec(0, 0, -1)
    p3 = p1 + vec(0, -1, 0)
    points = [p1, p2, p3]
    points_r = [rotz(theta, p) for p in points]
    geometry = make_regular_polygon(2*w, h, 4, points_r, parent=None)
    sampleholder.add_geometry(geometry)
    x, y, z = manipulator.origin
    manipx.set(x)
    manipy.set(y)
    # Sink manipz so that we are blocking beam
    manipz.set(z - h + 1)
    manipr.set(0)
    yield manipulator, angle
    sampleholder._reset()


@pytest.fixture(scope='function')
def RE(request):
    loop = asyncio.new_event_loop()
    loop.set_debug(True)
    RE = RunEngine({}, loop=loop, call_returns_result=True)
    RE = setup_run_engine(RE)

    def clean_event_loop():
        if RE.state not in ('idle', 'panicked'):
            try:
                RE.halt()
            except TransitionError:
                pass
        loop.call_soon_threadsafe(loop.stop)
        RE._th.join()
        loop.close()

    request.addfinalizer(clean_event_loop)
    return RE


# vendored from ophyd.sim
class NumpySeqHandler:
    specs = {'NPY_SEQ'}

    def __init__(self, filename, root=''):
        self._name = os.path.join(root, filename)

    def __call__(self, index):
        return np.load('{}_{}.npy'.format(self._name, index))

    def get_file_list(self, datum_kwarg_gen):
        "This method is optional. It is not needed for access, but for export."
        return ['{name}_{index}.npy'.format(name=self._name, **kwargs)
                for kwargs in datum_kwarg_gen]


@pytest.fixture(scope='function')
def db(request):
    """Return a data broker
    """
    from databroker import temp
    db = temp()
    return db
