import pygame
import random


class Map:
    def __init__(self, map_image_path, cell_size=32):
        self.cell_size = cell_size
        self.image = pygame.image.load(map_image_path).convert()
        self.width, self.height = self.image.get_size()
        self.cols = self.width // cell_size
        self.rows = self.height // cell_size

        # Initialize the walkability grid (0 = walkable, 1 = blocked)
        self.walkability = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.chest_spots = []
        self.enemy_spawns = []

        self._generate_grid()

    def _generate_grid(self):
        """Populates the walkability grid and identifies spawn points."""
        for row in range(self.rows):
            for col in range(self.cols):
                # Calculate the center of the cell
                sample_x = col * self.cell_size + self.cell_size // 2
                sample_y = row * self.cell_size + self.cell_size // 2
                color = self.image.get_at((sample_x, sample_y))[:3]

                # If the color is black, mark as blocked.
                # You might adjust the threshold if needed.
                if color == (0, 0, 0):
                    self.walkability[row][col] = 1
                else:
                    self.walkability[row][col] = 0

                # Optional: check for special colors for chest and enemy spawns
                # For example, if color is light pink, add to chest_spots.
                # if color == (255, 182, 193):  # light pink
                #     self.chest_spots.append((sample_x, sample_y))
                # Similarly for enemy spawns...

    def is_cell_walkable(self, pixel_x, pixel_y):
        """Converts pixel coordinates to grid coordinates and checks walkability."""
        grid_col = int(pixel_x) // self.cell_size
        grid_row = int(pixel_y) // self.cell_size
        # Ensure the coordinates are within bounds
        if 0 <= grid_col < self.cols and 0 <= grid_row < self.rows:
            return self.walkability[grid_row][grid_col] == 0
        return False

    def get_random_chest_spots(self, n):
        """Returns n random chest positions."""
        return random.sample(self.chest_spots, k=min(n, len(self.chest_spots)))

    def get_random_enemy_spawns(self, n):
        """Returns n random enemy spawn positions."""
        return random.sample(self.enemy_spawns, k=min(n, len(self.enemy_spawns)))

    def draw_debug(self, screen):
        """Optional debug method to draw grid lines and obstacles."""
        for row in range(self.rows):
            for col in range(self.cols):
                rect = pygame.Rect(col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size)
                # Draw grid cell borders
                pygame.draw.rect(screen, (100, 100, 100), rect, 1)
                # If blocked, fill with a transparent overlay
                if self.walkability[row][col] == 1:
                    s = pygame.Surface((self.cell_size, self.cell_size))
                    s.set_alpha(100)
                    s.fill((0, 0, 0))
                    screen.blit(s, rect.topleft)
