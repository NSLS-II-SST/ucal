from bl_funcs.re_commands import generic_cmd


def load_RE_commands(engine):
    engine.register_command("calibrate", generic_cmd)
    engine.register_command("set_frame_sample_center", generic_cmd)
    engine.register_command("set_frame_sample_edge", generic_cmd)


def setup_run_engine(engine):
    """
    Function that yields a fully set-up and ready-to-go run engine
    """
    load_RE_commands(engine)
    return engine
