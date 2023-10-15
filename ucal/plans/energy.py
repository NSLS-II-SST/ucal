import bluesky.plan_stubs as bps
from ucal.energy import en
from ucal_hw.energy import base_grating_to_250, base_grating_to_1200
from ucal.detectors import ref
from ucal.multimesh import set_ref
from sst_funcs.gGrEqns import get_mirror_grating_angles, find_best_offsets
from sst_funcs.plans.maximizers import find_max
from bluesky.plans import rel_scan
from sst_funcs.configuration import add_to_plan_list

def tune_pgm(cs=[1.45, 1.5, 1.55, 1.6],
             ms=[1, 1, 1, 1],
             energy=291.65,
             pol=0,
             k=250):
    # RE(load_sample(sample_by_name(bar, 'HOPG')))
    # RE(tune_pgm(cs=[1.35,1.37,1.385,1.4,1.425,1.45],ms=[1,1,1,1,1],energy=291.65,pol=90,k=250))
    # RE(tune_pgm(cs=[1.55,1.6,1.65,1.7,1.75,1.8],ms=[1,1,1,1,1],energy=291.65,pol=90,k=1200))

    yield from bps.mv(en.polarization, pol)
    yield from bps.mv(en, energy)
    mirror_measured = []
    grating_measured = []
    energy_measured = []
    m_measured = []
    grating = en.monoen.grating
    mirror2 = en.monoen.mirror2
    
    for cff, m_order in zip(cs, ms):
        m_set, g_set = get_mirror_grating_angles(energy, cff, k, m_order)
        yield from bps.mv(grating, g_set, mirror2, m_set, grating.velocity, 0.1, mirror2.velocity, 0.1)
        yield from bps.sleep(0.2)
        _ = yield from find_max(rel_scan, [ref], grating, -0.1, 0.1, 41, max_channel=ref.name)
        ret = yield from find_max(rel_scan, [ref], grating, -0.015, 0.015, 61, max_channel=ref.name)
        _, gmax = ret[0]
        grating_measured.append(gmax)
        mirror_measured.append(m_set)
        energy_measured.append(energy)
        m_measured.append(m_order)
    print(f"mirror positions: {mirror_measured}")
    print(f"grating positions: {grating_measured}")
    print(f"energy positions: {energy_measured}")
    print(f"orders: {m_measured}")
    print(f"Current Mir2 Offset: {mirror2.user_offset.get()}")
    print(f"Current Grating Offset: {grating.user_offset.get()}")
    fit = find_best_offsets(mirror_measured, grating_measured, m_measured, energy_measured, k)
    print(fit)
    accept = input("Accept these values and set the offset (y/n)? ")
    if accept in ["y", "Y", "yes"]:
        yield from bps.mvr(mirror2.user_offset, -fit.x[0], grating.user_offset, -fit.x[1])
    return fit

def tune_250():
    yield from set_ref(1)
    yield from tune_pgm(cs=[1.45, 1.5, 1.55, 1.6],
                        ms=[1, 1, 1, 1],
                        energy=291.65,
                        pol=0,
                        k=250)

def tune_1200():
    yield from set_ref(1)
    yield from tune_pgm(cs=[2.0, 2.05, 2.1, 2.15],
                        ms=[1, 1, 1, 1],
                        energy=291.65,
                        pol=0,
                        k=1200)

@add_to_plan_list
def tune_grating():
    grating = yield from bps.rd(en.monoen.gratingx.readback)
    if "250l/mm" in grating:
        yield from tune_250()
    elif "1200l/mm" in grating:
        yield from tune_1200()
    else:
        print("Grating must be either 250/mm or 1200l/mm")
    
@add_to_plan_list
def change_grating(grating, tune=True):
    if grating == 250:
        yield from base_grating_to_250()
        if tune:
            yield from tune_250()
    elif grating == 1200:
        yield from base_grating_to_1200()
        if tune:
            yield from tune_1200()
    else:
        print("Grating not understood, value must be one of [250, 1200]")
