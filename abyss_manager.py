import time
import pygame as pg
from config import Config  # assumes you’ve defined TILE_SIZE, SCREEN_WIDTH, MAP_LAYOUT
from abyss_map import Map  # your Map class with chest/enemy/walkable logic
from abyss_camera import Camera  # basic camera that applies offsets
from abyss_player import Player


class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.tile_size = Config.TILE_SIZE
        self.stage_keys = list(Config.MAP_LAYOUT.keys())  # e.g., ["stage 1", "stage 2", "stage 3"]
        self.current_stage_index = 0

        self.map = None
        self.camera = None
        self.enemies = []
        self.player = Player(spawn_point=(self.tile_size * 74, self.tile_size * 55), map_ref=self.map)

        self.active_aoes = []

        self.load_stage(self.stage_keys[self.current_stage_index])

    def load_stage(self, stage_key):
        map_path = Config.MAP_LAYOUT[stage_key]
        self.map = Map(map_path, self.tile_size)
        self.camera = Camera(Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        self.player = Player(spawn_point=(self.tile_size * 74, self.tile_size * 55), map_ref=self.map)  # reset position

    def advance_stage(self):
        self.current_stage_index += 1
        if self.current_stage_index < len(self.stage_keys):
            self.load_stage(self.stage_keys[self.current_stage_index])
        else:
            print("All stages completed.")

    def update(self):
        aoe = self.player.update(self.enemies)
        self.camera.update(self.player.position)
        if aoe:
            self.active_aoes.append(aoe)

        # For each enemy that can cast:
        for enemy in self.enemies:
            aoe = enemy.update(self.player)
            if aoe:
                self.active_aoes.append(aoe)

        self.active_aoes = [aoe for aoe in self.active_aoes if not aoe.is_expired()]

    def draw(self):
        self.map.draw_placeholder(self.screen, self.camera, floor=True)
        for aoe in self.active_aoes:
            aoe.draw(self.screen, self.camera)
        self.map.draw_placeholder(self.screen, self.camera, wall=True)

        px, py = self.camera.apply(self.player.position)
        pg.draw.rect(self.screen, (0, 0, 255), (px, py, self.player.size, self.player.size))
        self.draw_state_label(self.screen)

    def draw_state_label(self, surface):
        pg.font.init()
        font = pg.font.SysFont("arial", 20)
        state_text = f"State: {self.player.state}"
        label = font.render(state_text, True, (255, 255, 255))  # white text
        surface.blit(label, (10, Config.SCREEN_HEIGHT - 30))  # 10px from left, 30px from bottom


def main():
    pg.init()
    pg.font.init()
    font = pg.font.SysFont("arial", 20)

    screen = pg.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
    pg.display.set_caption("Abyss Slayer")
    clock = pg.time.Clock()

    gm = GameManager(screen)

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        gm.update()
        screen.fill((0, 0, 0))
        gm.draw()
        pg.display.flip()
        clock.tick(60)

    pg.quit()

if __name__ == "__main__":
    main()