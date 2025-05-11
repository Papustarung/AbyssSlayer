import pygame as pg
import math
from abyss_utils import circle_rect_collision

class Projectile:
    def __init__(self, caster, position, direction, radius=4, speed=10.0, base_damage=20, multiplier=0.75):
        """
        caster     : Entity that fired it (used for team, damage, amplification)
        position   : (x, y) starting center position
        direction  : normalized (dx, dy) vector
        radius     : visual and collision size
        speed      : movement speed in pixels/frame
        base_damage: raw attack stat (caster.attack)
        """
        self.caster = caster
        self.position = list(position)
        self.direction = direction
        self.radius = radius
        self.speed = speed
        self.base_damage = base_damage
        self.multiplier = multiplier

        self.angle = math.degrees(math.atan2(-self.direction[1], self.direction[0]))
        self.length = 24
        self.width = 4

        # Amplified damage
        amp = caster.amplifiers.get("projectile", 0)
        self.damage = base_damage * (1 + amp / 100) * self.multiplier

        self.active = True

    def update(self, wall_rects, targets):
        if not self.active:
            return

        # Move
        self.position[0] += self.direction[0] * self.speed
        self.position[1] += self.direction[1] * self.speed

        # Check wall collision
        rect = pg.Rect(self.position[0] - self.radius, self.position[1] - self.radius,
                       self.radius * 2, self.radius * 2)
        for wall in wall_rects:
            if rect.colliderect(wall):
                print(f"Projectile hit wall")
                self.active = False
                return

        # Check target collision
        for target in targets:
            if not target or target.state == "dead":
                continue
            if target.team_id == self.caster.team_id:
                continue

            if circle_rect_collision(self.position, self.radius, target.get_rect()):
                target.take_damage(self.damage, self.caster)
                print(f"{self.caster.team_id} deal {self.damage:.1f} damage (Projectile)")
                self.active = False
                return

    def draw(self, surface, camera, color=(255, 255, 0), outline_color=(0, 0, 0)):
        if not self.active:
            return

        cx, cy = camera.apply(self.position)
        center = (int(cx), int(cy))
        radius = self.radius

        # Draw outline first
        pg.draw.circle(surface, outline_color, center, radius + 1)

        # Draw inner projectile
        pg.draw.circle(surface, color, center, radius)


