import math
import time
import pygame as pg

class AOEAttack:
    def __init__(self, caster, generated_pos, base_radius=128, multiplier=1.0, target_type="enemy"):
        self.caster = caster
        self.generated_pos = generated_pos
        self.base_radius = base_radius
        self.multiplier = multiplier
        self.target_type = target_type
        self.start_time = time.time()
        self.lifetime = 0.5

        # Final radius with scroll amplifier
        amp = caster.amplifiers.get("aoe", 0)
        self.radius = base_radius + amp

    def apply_to_targets(self, targets):
        cx, cy = self.generated_pos

        for target in targets:
            if target.state == "dead":
                continue
            if self.target_type == "enemy" and target.team_id == self.caster.team_id:
                continue
            if self.target_type == "player" and target.team_id != "player":
                continue

            tx, ty = target.position
            distance = math.hypot(cx - tx, cy - ty)

            if distance <= self.radius:
                final_dmg = self.caster.attack * self.multiplier
                target.take_damage(final_dmg, self.caster)

    def is_expired(self):
        return time.time() - self.start_time > self.lifetime

    def draw(self, surface, camera, color=(255, 100, 100), alpha=100):
        radius = int(self.radius)
        cx, cy = camera.apply(self.generated_pos)

        temp_surface = pg.Surface((radius * 2, radius * 2), pg.SRCALPHA)
        pg.draw.circle(temp_surface, (*color, alpha), (radius, radius), radius)
        surface.blit(temp_surface, (cx - radius, cy - radius))
