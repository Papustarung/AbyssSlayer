import pygame as pg
from config import Config

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

    def apply_rect(self, rect):
        return rect.move(-self.offset.x, -self.offset.y)

    def draw_visibility_mask(self, surface, player_center_world, radius=Config.DETECTION_DISTANCE, alpha=0.7):
        player_screen_pos = self.apply(player_center_world)

        width, height = surface.get_size()
        mask = pg.Surface((width, height), pg.SRCALPHA)
        mask.fill((15, 10, 5, int(255 * alpha)))

        pg.draw.circle(mask, (0, 0, 0, 0), (int(player_screen_pos[0]), int(player_screen_pos[1])), radius)
        surface.blit(mask, (0, 0))
