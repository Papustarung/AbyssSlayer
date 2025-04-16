import pygame as pg

class Camera:
    def __init__(self, screen_w, screen_h):
        self.offset = pg.Vector2(0, 0)
        self.screen_w = screen_w
        self.screen_h = screen_h

    def update(self, target_pos):
        self.offset.x = target_pos[0] - self.screen_w // 2
        self.offset.y = target_pos[1] - self.screen_h // 2

    def apply(self, pos):
        return int(pos[0] - self.offset.x), int(pos[1] - self.offset.y)