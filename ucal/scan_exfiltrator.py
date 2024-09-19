from nbs_bl.hw import manipulator


class ScanExfiltrator:
    def __init__(self, motor, energy):
        self.motor = motor
        self.start_energy = energy
        self.index = 0

    def get_scan_start_info(self):
        motor_name = getattr(self.motor, "name", "unnamed_motor")
        motor_unit = getattr(self.motor, "egu", "index")
        sample = manipulator.sample
        sample_id = sample.sample_id.get()
        sample_name = sample.sample_name.get()
        info = {
            "motor": motor_name,
            "motor_unit": motor_unit,
            "sample_id": sample_id,
            "sample_name": sample_name,
            "start_energy": self.start_energy,
        }
        return info

    def get_scan_point_info(self):
        pos = getattr(self.motor, "position", self.index)
        self.index += 1
        return pos
