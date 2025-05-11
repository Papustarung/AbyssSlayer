import pygame as pg
import time
from abyss_entity import Entity
from config import Config
from datalogger import DataLogger

class Player(Entity):
    def __init__(self, spawn_point, map_ref, game_manager=None):
        super().__init__(
            base_health=100,
            base_attack=20,
            base_defense=10,
            spawn_point=spawn_point,
            size=40
        )
        self.speed = 4.0
        self.team_id = "player"
        self.map = map_ref

        self.projectile_speed = 24.0
        self.projectile_cooldown = 0.5
        self.attack = 20

        self.game_manager = game_manager

    def take_damage(self, dmg, attacker):
        if self.invincible or self.state == Entity.DEAD:
            return

        flat_damage = getattr(attacker, "flat_damage", 0)
        buff_bonus = attacker.active_buffs.get("damage", {}).get("value", 0)
        total_flat = flat_damage + buff_bonus + Config.FLAT_DMG

        damage_taken = dmg * (dmg / (self.defense + dmg)) + total_flat
        self.health -= damage_taken

        self.game_manager.damage_logger.log(
            "damage_taken",
            damage=dmg
        )

        self.invincible = True
        self.invincible_start = time.time()

        if self.health <= 0:
            self.die()
        else:
            health_left = self.health/self.max_health
            red = int(255*(1-health_left))
            green = int(255*health_left)
            self.health_color = (red, green, 0)

    def process_input(self):
        keys = pg.key.get_pressed()
        dx = dy = 0
        apply_buff = False
        cast_aoe = False
        shoot_projectile = False
        mouse_dir = None

        if self.state != "casting":
            if keys[pg.K_w]: dy -= 1
            if keys[pg.K_s]: dy += 1
            if keys[pg.K_a]: dx -= 1
            if keys[pg.K_d]: dx += 1

            if keys[pg.K_r]:
                apply_buff = True

            if keys[pg.K_q]:
                cast_aoe = True

            if keys[pg.K_e]:
                mouse_pos = pg.mouse.get_pos()
                world_mouse = pg.Vector2(mouse_pos[0], mouse_pos[1]) + self.camera.offset
                dir_vec = pg.Vector2(world_mouse[0] - self.center[0], world_mouse[1] - self.center[1])
                if dir_vec.length() != 0:
                    mouse_dir = dir_vec.normalize()
                    shoot_projectile = True

        return dx, dy, apply_buff, cast_aoe, shoot_projectile, mouse_dir

    def handle_movement(self, dx, dy, wall_rects):
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            scale = 1 / (2 ** 0.5)
            dx *= scale
            dy *= scale

        speed = self.speed + self.active_buffs.get("speed", {}).get("value", 0)
        rect = pg.Rect(self.position[0], self.position[1], self.size, self.size)

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

        self.position = (rect.x, rect.y)
        self.update_center()

    def update(self, targets, camera):
        self.camera = camera
        super().update()

        dx, dy, cast_aoe, apply_buff, shoot_projectile, mouse_dir = self.process_input()

        # if interact:
        #     scroll = interactions.try_interact()
        #     if scroll:
        #         self.apply_scroll(scroll)

        if cast_aoe and self.can_use_aoe():
            return self.use_aoe(targets, self.center)  # return AOEAttack for rendering

        if shoot_projectile and mouse_dir and self.can_use_projectile():
            return self.use_projectile(mouse_dir)

        if apply_buff and self.can_use_buff():
            self.use_buff()

        # movement + state logic
        if self.state != "casting":
            self.handle_movement(dx, dy, self.map.get_wall_rects())

        # state logic
        if self.state != "casting":
            if dx != 0 or dy != 0:
                self.state = "moving"
            else:
                self.state = "idle"

        if self.pending_projectile:
            proj = self.pending_projectile
            self.pending_projectile = None
            return proj


