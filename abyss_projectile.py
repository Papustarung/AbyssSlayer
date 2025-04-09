class Projectile:
    def __init__(self, caster, position, radius, dmg_add):
        self.caster = caster
        self.generated_pos = position
        self.bonus = dmg_add
        self.radius = radius
        self.multiplier = 1.5
        self.cooldown = 1.0

    def cast(self, direction):
        pass