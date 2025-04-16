import pygame
import sys
from PIL import Image

# --- Settings ---
TILE_SIZE = 32
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
PLAYER_SIZE = 40
PLAYER_SPEED = 4

# --- Load Grid from Image ---
def load_grid_from_image(image_path, tile_size=32):
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    grid = []
    for y in range(height // tile_size):
        row = []
        for x in range(width // tile_size):
            px = x * tile_size + tile_size // 2
            py = y * tile_size + tile_size // 2
            r, g, b = img.getpixel((px, py))
            if (r, g, b) == (0, 0, 0):
                row.append('1')  # Wall
            elif (r, g, b) == (255, 255, 255):
                row.append('0')  # Floor
            elif (r, g, b) == (255, 0, 0):
                row.append('E')  # Enemy Spawn
            elif (r, g, b) == (0, 255, 0):
                row.append('C')  # Chest
            else:
                row.append('0')
        grid.append(row)
    return grid

# --- Map Class ---
class Map:
    def __init__(self, grid, tile_size):
        self.grid = grid
        self.tile_size = tile_size

    def draw(self, surface, camera):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                world_x = x * self.tile_size
                world_y = y * self.tile_size
                screen_x, screen_y = camera.apply((world_x, world_y))
                rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)
                if cell == '1':
                    pygame.draw.rect(surface, (0, 0, 0), rect)
                elif cell == 'E':
                    pygame.draw.rect(surface, (255, 0, 0), rect)
                elif cell == 'C':
                    pygame.draw.rect(surface, (0, 255, 0), rect)
                else:
                    pygame.draw.rect(surface, (255, 255, 255), rect)

    def get_wall_rects(self):
        walls = []
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == '1':
                    walls.append(pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size))
        return walls

# --- Camera Class ---
class Camera:
    def __init__(self, screen_w, screen_h):
        self.offset = pygame.Vector2(0, 0)
        self.screen_w = screen_w
        self.screen_h = screen_h

    def update(self, target_pos):
        self.offset.x = target_pos[0] - self.screen_w // 2
        self.offset.y = target_pos[1] - self.screen_h // 2

    def apply(self, pos):
        return int(pos[0] - self.offset.x), int(pos[1] - self.offset.y)

# --- Main Function ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("AABB Collision Test")
    clock = pygame.time.Clock()

    # Load map
    grid = load_grid_from_image("assets/maps/abyss_map_layout_1.png", TILE_SIZE)
    game_map = Map(grid, TILE_SIZE)
    wall_rects = game_map.get_wall_rects()

    # Initialize player
    player_pos = [TILE_SIZE * 74.0, TILE_SIZE * 54.0]
    player_rect = pygame.Rect(int(player_pos[0]), int(player_pos[1]), PLAYER_SIZE, PLAYER_SIZE)
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_a]: dx -= PLAYER_SPEED
        if keys[pygame.K_d]: dx += PLAYER_SPEED
        if keys[pygame.K_w]: dy -= PLAYER_SPEED
        if keys[pygame.K_s]: dy += PLAYER_SPEED

        if dx != 0 and dy != 0:
            scale = 1 / (2 ** 0.5)
            dx *= scale
            dy *= scale

        # Horizontal movement with collision
        player_rect.x += int(dx)
        for wall in wall_rects:
            if player_rect.colliderect(wall):
                if dx > 0:
                    player_rect.right = wall.left
                elif dx < 0:
                    player_rect.left = wall.right

        # Vertical movement with collision
        player_rect.y += int(dy)
        for wall in wall_rects:
            if player_rect.colliderect(wall):
                if dy > 0:
                    player_rect.bottom = wall.top
                elif dy < 0:
                    player_rect.top = wall.bottom

        # Update float position for smooth camera
        player_pos[0] = float(player_rect.x)
        player_pos[1] = float(player_rect.y)
        camera.update(player_pos)

        # Draw everything
        screen.fill((255, 255, 255))
        game_map.draw(screen, camera)
        px, py = camera.apply(player_rect.topleft)
        pygame.draw.rect(screen, (0, 0, 255), (px, py, PLAYER_SIZE, PLAYER_SIZE))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

# Run it locally with your image file
# main()

if __name__ == "__main__":
    main()
