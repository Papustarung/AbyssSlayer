from abyss_entity import Entity
import pygame as pg

class Player(Entity):
    def __init__(self, spawn_point, map_ref):
        super().__init__(
            base_health=100,
            base_attack=20,
            base_defense=10,
            spawn_point=spawn_point,
            size=40
        )
        self.team_id = "player"
        self.map = map_ref

    def process_input(self):
        keys = pg.key.get_pressed()
        dx = dy = 0
        cast_aoe = False

        if self.state != "casting":
            if keys[pg.K_w]: dy -= 1
            if keys[pg.K_s]: dy += 1
            if keys[pg.K_a]: dx -= 1
            if keys[pg.K_d]: dx += 1

            if keys[pg.K_e]:
                cast_aoe = True

        return dx, dy, cast_aoe

    def handle_movement(self, dx, dy, wall_rects):
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            scale = 1 / (2 ** 0.5)
            dx *= scale
            dy *= scale

        speed = self.speed + self.active_buffs.get("speed", {}).get("value", 0)
        rect = pg.Rect(self.position[0], self.position[1], self.size, self.size)
        self.update_center()

        # Horizontal collision
        rect.x += int(dx * speed)
        for wall in wall_rects:
            if rect.colliderect(wall):
                if dx > 0:
                    rect.right = wall.left
                elif dx < 0:
                    rect.left = wall.right

        # Vertical collision
        rect.y += int(dy * speed)
        for wall in wall_rects:
            if rect.colliderect(wall):
                if dy > 0:
                    rect.bottom = wall.top
                elif dy < 0:
                    rect.top = wall.bottom

        if self.state != "casting":  # only update state if not casting
            if dx != 0 or dy != 0:
                self.state = "moving"
            else:
                self.state = "idle"

        self.position = (rect.x, rect.y)

    def update(self, targets):
        super().update()

        dx, dy, cast_aoe = self.process_input()

        # movement + state logic
        if self.state != "casting":
            self.handle_movement(dx, dy, self.map.get_wall_rects())

        # state logic
        if self.state != "casting":
            if dx != 0 or dy != 0:
                self.state = "moving"
            else:
                self.state = "idle"

        if cast_aoe and self.can_use_aoe():
            return self.use_aoe(targets)  # return AOEAttack for rendering


