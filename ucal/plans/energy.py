import bluesky.plan_stubs as bps
from ucal.hw import en, ref, psh4
from .plan_stubs import set_edge
from nbs_bl.plans.plan_stubs import set_exposure
from nbs_bl.gGrEqns import get_mirror_grating_angles, find_best_offsets
from nbs_bl.plans.maximizers import find_max, fly_max
from bluesky.plans import rel_scan
from nbs_bl.help import add_to_plan_list


def base_grating_to_250(stripe=2):
    mono_en = en.monoen
    stripe_str = mono_en.gratingx.setpoint.enum_strs[stripe]
    current_stripe = mono_en.gratingx.readback.get()
    if "250" not in stripe_str:
        print(f"Requested stripe {stripe_str} is not a 250l/mm stripe, aborting setup")
        return 0
    if current_stripe != stripe_str:
        print(f"Moving the grating to {stripe_str}.  This will take a minute...")
        yield from psh4.close()
        yield from bps.abs_set(mono_en.gratingx, stripe, wait=True)
    else:
        print(f"the grating is already at {current_stripe}")

    # yield from bps.sleep(60)
    # yield from bps.mv(mirror2.user_offset, 0.04) #0.0315)
    # yield from bps.mv(grating.user_offset, -0.0874)#-0.0959)
    # yield from bps.mv(en.m3offset, 7.91)
    yield from bps.mv(mono_en.cff, 1.47)
    yield from bps.mv(en, 270)
    yield from psh4.open()
    print(
        f"the grating is now at {stripe_str}, signifigant higher order beam will be present"
    )
    return 1


def base_grating_to_1200(stripe=9):
    mono_en = en.monoen
    stripe_str = mono_en.gratingx.setpoint.enum_strs[stripe]
    current_stripe = mono_en.gratingx.readback.get()
    if "1200" not in stripe_str:
        print(f"Requested stripe {stripe_str} is not a 1200l/mm stripe, aborting setup")
        return 0
    if current_stripe != stripe_str:
        print(f"Moving the grating to {stripe_str}.  This will take a minute...")
        yield from psh4.close()
        yield from bps.abs_set(mono_en.gratingx, stripe, wait=True)
    else:
        print(f"the grating is already at {current_stripe}")
    # yield from bps.sleep(60)
    # yield from bps.mv(mirror2.user_offset, 0.2044) #0.1962) #0.2052) # 0.1745)  # 8.1264)
    # yield from bps.mv(grating.user_offset, 0.0769) #0.0687) # 0.0777) # 0.047)  # 7.2964)  # 7.2948)#7.2956
    yield from bps.mv(mono_en.cff, 2.02)
    # yield from bps.mv(en.m3offset, 7.91)
    yield from bps.mv(en, 270)
    yield from psh4.open()
    print(f"the grating is now at {stripe_str}")
    return 1


def setup_mono():
    mono_en = en.monoen
    monotype = mono_en.gratingx.readback.get()
    if "250l/mm" in monotype:
        # yield from bps.mv(en.m3offset, 7.91)
        yield from bps.mv(mono_en.cff, 1.47)
    elif "1200" in monotype:
        yield from bps.mv(mono_en.cff, 2.02)
        # yield from bps.mv(en.m3offset, 7.91)


def tune_pgm(
    cs=[1.45, 1.5, 1.55, 1.6],
    ms=[1, 1, 1, 1],
    energy=291.65,
    pol=0,
    k=250,
    auto_accept=True,
):
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
        yield from bps.mv(
            grating, g_set, mirror2, m_set, grating.velocity, 0.1, mirror2.velocity, 0.1
        )
        yield from bps.sleep(0.2)
        max_info = yield from fly_max(
            [ref], grating, g_set - 0.1, g_set + 0.1, 0.2 / 30, period=0.2
        )
        gset2 = max_info[ref.name][grating.name]
        max_info = yield from fly_max(
            [ref], grating, gset2 - 0.015, gset2 + 0.015, 0.03 / 30.0, period=0.2
        )
        gmax = max_info[ref.name][grating.name]
        """
        _ = yield from find_max(
            rel_scan, [ref], grating, -0.1, 0.1, 41, max_channel=ref.name
        )
        ret = yield from find_max(
            rel_scan, [ref], grating, -0.015, 0.015, 61, max_channel=ref.name
        )
        _, gmax = ret[0]
        """
        grating_measured.append(gmax)
        mirror_measured.append(m_set)
        energy_measured.append(energy)
        m_measured.append(m_order)
    print(f"mirror positions: {mirror_measured}")
    print(f"grating positions: {grating_measured}")
    print(f"energy positions: {energy_measured}")
    print(f"orders: {m_measured}")
    mir2_current = mirror2.user_offset.get()
    grat_current = grating.user_offset.get()
    fit = find_best_offsets(
        mirror_measured, grating_measured, m_measured, energy_measured, k
    )
    print(f"Current Mir2 Offset: {mir2_current}, New Offset: {mir2_current - fit.x[0]}")
    print(
        f"Current Grating Offset: {grat_current}, New Offset: {grat_current - fit.x[1]}"
    )

    print(f"Fit object: {fit}")

    if not auto_accept:
        accept = input("Accept these values and set the offset (y/n)? ")
    else:
        accept = "y"
    if accept in ["y", "Y", "yes"]:
        yield from bps.mvr(
            mirror2.user_offset, -fit.x[0], grating.user_offset, -fit.x[1]
        )
    return fit


def tune_250(auto_accept=True):
    yield from set_edge("1")
    yield from tune_pgm(
        cs=[1.4, 1.45, 1.5, 1.55],
        ms=[1, 1, 1, 1],
        energy=291.65,
        pol=0,
        k=250,
        auto_accept=auto_accept,
    )


def tune_1200(auto_accept=True):
    yield from set_edge("1")
    yield from tune_pgm(
        cs=[2.0, 2.05, 2.1, 2.15],
        ms=[1, 1, 1, 1],
        energy=291.65,
        pol=0,
        k=1200,
        auto_accept=auto_accept,
    )


@add_to_plan_list
def tune_grating(auto_accept=True):
    """Tune grating offsets, should be run after grating change automatically"""
    grating = yield from bps.rd(en.monoen.gratingx.readback)
    yield from set_exposure(1.0)
    if "250l/mm" in grating:
        print("Tuning 250l/mm Grating")
        yield from setup_mono()
        yield from tune_250(auto_accept=auto_accept)
    elif "1200l/mm" in grating:
        print("Tuning 1200l/mm Grating")
        yield from setup_mono()
        yield from tune_1200(auto_accept=auto_accept)
    else:
        print("Grating must be either 250/mm or 1200l/mm")


@add_to_plan_list
def change_grating(stripe, tune=True):
    """Change to specified grating, optionally tune afterwards

    grating: either 250 or 1200
    tune: if True, calibrate grating offsets after change"""
    mono_en = en.monoen
    if isinstance(stripe, int):
        stripe_str = mono_en.gratingx.setpoint.enum_strs[stripe]
    else:
        stripe_str = stripe
        stripe = mono_en.gratingx.setpoint.enum_strs.index(stripe_str)
    if "250" in stripe_str:
        yield from base_grating_to_250(stripe)
        if tune:
            yield from tune_250()
    elif "1200" in stripe_str:
        yield from base_grating_to_1200(stripe)
        if tune:
            yield from tune_1200()
    else:
        print("Grating not understood, value must be one of [250, 1200]")
