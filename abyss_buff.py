import time

class Buff:
    def __init__(self, caster, buff_type: str, value: float, duration: float):
        self.caster = caster
        self.buff_type = buff_type
        self.value = value
        self.duration = duration
        self.start_time = time.time()

    def is_active(self):
        return (time.time() - self.start_time) < self.duration

    def apply(self):
        self.caster.active_buffs[self.buff_type] = {
            "value": self.value,
            "start_time": self.start_time,
            "duration": self.duration
        }

    def remaining_time(self):
        return max(0.0, self.duration - (time.time() - self.start_time))
