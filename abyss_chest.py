import pygame as pg
from config import Config

class Chest:
    def __init__(self, position, scroll):
        self.position = position
        self.scroll = scroll  # one of "projectile", "aoe", "buff"
        self.opened = False
        self.size = Config.TILE_SIZE
        self.rect = pg.Rect(position[0], position[1], self.size, self.size)

    def interact(self, player):
        if self.opened:
            print("Chest already opened")
            return

        print("Chest.interact() called!")
        print(f"Giving scroll: {self.scroll}")

        self.opened = True
        player.obtain_scroll(self.scroll)
        print("Scroll given to player")

    def draw(self, surface, camera):
        screen_pos = camera.apply(self.position)
        color = (139, 69, 19) if not self.opened else (80, 80, 80)
        pg.draw.rect(surface, color, (*screen_pos, self.size, self.size))

    def __repr__(self):
        return str(self.position)

