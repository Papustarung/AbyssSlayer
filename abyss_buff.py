
class Buff:
    def __init__(self, duration_add):
        self.buff = (2.0, 5.0)
        self.duration = 5 + duration_add
        self.cooldown = 15.0

    def cast(self, target, type):
        if type == "speed":
            target.spd_buff = self.buff[0]
        elif type == "attack":
            target.atk_buff = self.buff[1]