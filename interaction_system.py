import pygame as pg
from config import Config

class InteractionSystem:
    def __init__(self, chests):
        self.chests = chests
        self.key_cooldown = 0  # for debounce

    def update(self, player):
        keys = pg.key.get_pressed()
        if keys[pg.K_f] and self.key_cooldown <= 0:
            for chest in self.chests:
                if not chest.opened and self._is_near(player, chest):
                    chest.interact(player)
                    self.key_cooldown = 10  # frames before next interaction allowed
                    break

        if self.key_cooldown > 0:
            self.key_cooldown -= 1

    def _is_near(self, player, chest):
        px, py = player.center
        tile_x = int(px // Config.TILE_SIZE)
        tile_y = int(py // Config.TILE_SIZE)

        chest_tile_x = chest.rect.x // Config.TILE_SIZE
        chest_tile_y = chest.rect.y // Config.TILE_SIZE

        return (tile_x, tile_y) == (chest_tile_x, chest_tile_y)
        # player_rect = pg.Rect(player.position[0], player.position[1], player.size, player.size)
        # return player_rect.colliderect(chest.rect)


