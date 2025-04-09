
class AOEAttack:
    def __init__(self, caster, position, base_radius, radius_add):
        self.caster = caster
        self.generated_pos = position
        self.bonus = radius_add
        self.base_radius = base_radius
        self.multiplier = 3.0
        self.cooldown = 5.0

    def cast(self):
        pass