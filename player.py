import pygame as pg
import time
from config import Config
import math


class GameObject:
    def __init__(self, position, size, animator=None, image=None, color=None):
        self.position = position
        self.size = size
        self.animator = animator      # Optional: animated sprite
        self.image = image            # Optional: static sprite
        self.color = color            # Optional: fallback rectangle color

    def update(self):
        if self.animator:
            self.animator.update()

    def draw(self, screen):
        if self.animator:
            self.animator.draw(screen, self.position)
        elif self.image:
            screen.blit(self.image, self.position)
        elif self.color:
            pg.draw.rect(screen, self.color, (*self.position, self.size, self.size))


class Player(Entity):
    def __init__(self, base_health, base_attack, base_defense, spawn_point, size, stat_multiplier=1.0):
        super().__init__(base_health, base_attack, base_defense, spawn_point, size, stat_multiplier=1.0)
        self.term_id = "player"
        self.flat_damage = 2.0

    def get_input_direction(self):
        keys = pg.key.get_pressed()
        dx, dy = 0, 0

        if keys[pg.K_w]: dy -= 1
        if keys[pg.K_s]: dy += 1
        if keys[pg.K_a]: dx -= 1
        if keys[pg.K_d]: dx += 1

        length = math.hypot(dx, dy)
        if length > 0:
            dx /= length
            dy /= length

        return dx, dy

    def move(self, direction, game_map):
        dx, dy = direction
        next_x = self.position[0] + dx * (self.speed + self.spd_buff)
        next_y = self.position[1] + dy * (self.speed + self.spd_buff)

        if game_map.is_walkable(next_x, next_y):
            self.position = (next_x, next_y)





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