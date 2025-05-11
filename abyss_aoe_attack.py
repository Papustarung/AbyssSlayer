import math
import time
import pygame as pg
from abyss_utils import circle_rect_collision

class AOEAttack:
    def __init__(self, caster, generated_pos, base_radius=48, multiplier=1.5, target_type="enemy"):
        self.caster = caster
        self.generated_pos = generated_pos
        self.base_radius = base_radius
        self.multiplier = multiplier
        self.target_type = target_type
        self.start_time = time.time()
        self.lifetime = 1.0
        self.inner_radius = base_radius // 2
        self.dr = self.base_radius - self.inner_radius
        self.prev_time = time.time()

        # Final radius with scroll amplifier
        amp = caster.amplifiers.get("aoe", 0)
        self.radius = base_radius + amp

    def apply_to_targets(self, targets):

        for target in targets:
            if target.state == "dead":
                continue
            if self.target_type == "enemy" and target.team_id == self.caster.team_id:
                continue
            if self.target_type == "player" and target.team_id != "player":
                continue

            if circle_rect_collision(self.generated_pos, self.radius, target.get_rect()):
                final_dmg = self.caster.attack * self.multiplier * (1 + self.caster.amplifiers["aoe"] / 100)
                target.take_damage(final_dmg, self.caster)

    def is_expired(self):
        return time.time() - self.start_time > self.lifetime

    def update(self):
        if self.inner_radius < self.radius:
            self.inner_radius += self.dr / self.lifetime * 1/60

    def draw(self, surface, camera, color=(255, 100, 100), alpha=100):
        radius = int(self.radius)
        inner = int(self.inner_radius)
        cx, cy = camera.apply(self.generated_pos)

        temp_surface = pg.Surface((radius * 2, radius * 2), pg.SRCALPHA)
        inner_temp = pg.Surface((inner * 2, inner * 2), pg.SRCALPHA)
        pg.draw.circle(temp_surface, (*color, alpha), (radius, radius), radius)
        surface.blit(temp_surface, (cx - radius, cy - radius))
        pg.draw.circle(inner_temp, (*color, alpha), (inner, inner), inner)
        surface.blit(inner_temp, (cx - inner, cy - inner))
