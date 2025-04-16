import pygame as pg
from PIL import Image

class Map:

    FLOOR = '0'
    WALL = '1'
    ENEMY_SPAWN = 'E'
    CHEST_SPAWN = 'C'

    def __init__(self, image_path, tile_size):
        self.tile_size = tile_size
        self.grid = self._load_grid_from_image(image_path)
        self.walkable = []
        self.chest_spawns = []
        self.enemy_spawns = []
        self._process_layout()

    def _load_grid_from_image(self, image_path):
        img = Image.open(image_path).convert("RGB")
        width, height = img.size
        grid = []

        for y in range(height // self.tile_size):
            row = []
            for x in range(width // self.tile_size):
                px = x * self.tile_size + self.tile_size // 2
                py = y * self.tile_size + self.tile_size // 2
                r, g, b = img.getpixel((px, py))

                if (r, g, b) == (0, 0, 0):  # black = wall
                    row.append(Map.WALL)
                elif (r, g, b) == (255, 255, 255):  # white = floor
                    row.append(Map.FLOOR)
                elif (r, g, b) == (255, 0, 0):  # red = enemy zone
                    row.append(Map.ENEMY_SPAWN)
                elif (r, g, b) == (0, 255, 0):  # green = chest zone
                    row.append(Map.CHEST_SPAWN)
                else:
                    row.append(Map.WALL)  # default to walkable
            grid.append(row)
        return grid

    def _process_layout(self):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell != Map.WALL:  # walkable if not a wall
                    self.walkable.append((x, y))
                if cell == Map.CHEST_SPAWN:
                    self.chest_spawns.append((x, y))
                if cell == Map.ENEMY_SPAWN:
                    self.enemy_spawns.append((x, y))

    def get_wall_rects(self):
        wall_rects = []
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == Map.WALL:
                    wall_rects.append(pg.Rect(
                        x * self.tile_size,
                        y * self.tile_size,
                        self.tile_size,
                        self.tile_size
                    ))
        return wall_rects

    def is_walkable(self, x, y):
        if 0 <= y < len(self.grid) and 0 <= x < len(self.grid[0]):
            return self.grid[y][x] != '1'
        return False

    def draw_placeholder(self, surface, camera, show_grid=True, wall=False, floor=False, enemy=False, chest=False):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                world_x = x * self.tile_size
                world_y = y * self.tile_size
                screen_x, screen_y = camera.apply((world_x, world_y))

                if show_grid:
                    rect = pg.Rect(screen_x, screen_y, self.tile_size, self.tile_size)

                    if cell == Map.WALL and wall == True:
                        pg.draw.rect(surface, (50, 50, 50), rect)      # Wall
                    elif cell == Map.ENEMY_SPAWN and enemy == True:
                        pg.draw.rect(surface, (200, 0, 0), rect)      # Enemy spawn
                    elif cell == Map.CHEST_SPAWN and chest == True:
                        pg.draw.rect(surface, (0, 200, 0), rect)      # Chest
                    elif cell == Map.FLOOR and floor == True:
                        pg.draw.rect(surface, (230, 230, 230), rect)  # Floor
