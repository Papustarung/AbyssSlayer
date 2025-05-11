import time
import math
import pygame as pg
from abyss_entity import Entity
from config import Config

class Enemy(Entity):
    def __init__(self, spawn_point, size, ai_type="melee", game_manager=None, stage_level=0):
        super().__init__(base_health=40, base_attack=10, base_defense=5,
                         spawn_point=spawn_point, size=size)
        self.team_id = "enemy"
        self.ai_type = ai_type
        self.last_decision_time = time.time()
        self.decision_delay = 1.0  # seconds between actions

        self.game = game_manager
        self.path = []
        self.path_index = 0
        self.path_update_timer = 0
        self.path_update_interval = 0.25
        self.goal_boundary_center = None
        self.last_tile = None
        self.current_tile = None
        self.last_goal_tile = None

    def update(self, player):
        super().update()
        if self.state == Entity.CASTING:
            return None

        now = time.time()
        dx = player.center[0] - self.center[0]
        dy = player.center[1] - self.center[1]
        dist = math.hypot(dx, dy)

        # Try attack decision
        if now - self.last_decision_time >= self.decision_delay:
            self.last_decision_time = now
            result = self.decide_action(player, dist, dx, dy)
            if result:
                return result

        # Tile positions
        tile_now = (
            int(self.center[0] // Config.TILE_SIZE),
            int(self.center[1] // Config.TILE_SIZE)
        )
        player_tile = (
            int(player.center[0] // Config.TILE_SIZE),
            int(player.center[1] // Config.TILE_SIZE)
        )

        # ✅ Path update: if left tile or forced by LOS failure
        if (
                now - self.path_update_timer >= self.path_update_interval
                and tile_now != self.current_tile
        ):
            self.path_update_timer = now
            self.current_tile = tile_now

            if self.last_goal_tile is None or player_tile != self.last_goal_tile:
                self.last_goal_tile = player_tile
                walkables = self.game.map.get_walkable_tiles()

                # Choose target zone based on enemy type
                if self.ai_type == "melee":
                    goal_tile = self.get_melee_dest_tile(player_tile, walkables)
                elif self.ai_type == "ranged":
                    goal_tile = self.get_ranged_dest_tile(player, player_tile, walkables)
                else:
                    goal_tile = player_tile

                if goal_tile is None:
                    goal_tile = player_tile

                if goal_tile:
                    self.path = self.game.pathfinder.find_path(self.get_current_tile(), goal_tile)
                    self.path_index = 0

                    # Optional: remove path reversal
                    if self.path and len(self.path) >= 2 and self.path[1] == self.last_tile:
                        self.path.pop(1)

        # Follow path
        if self.path and self.path_index < len(self.path):
            cell = self.path[self.path_index]
            target_px = (
                cell[0] * Config.TILE_SIZE + Config.TILE_SIZE // 2,
                cell[1] * Config.TILE_SIZE + Config.TILE_SIZE // 2
            )

            move_dx = target_px[0] - self.center[0]
            move_dy = target_px[1] - self.center[1]
            dist_to_next = math.hypot(move_dx, move_dy)

            if dist_to_next <= max(2.0, self.speed):
                # Snap to tile
                self.position = (
                    target_px[0] - self.size // 2,
                    target_px[1] - self.size // 2
                )
                self.update_center()

                self.last_tile = self.path[self.path_index]
                self.current_tile = self.path[self.path_index]

                self.path_index += 1
                self.state = Entity.IDLE
            else:
                self.move((move_dx / dist_to_next, move_dy / dist_to_next))
                self.state = Entity.MOVING
        elif self.state != Entity.CASTING:
            self.state = Entity.IDLE

        # Fallback: no path or finished path
        if not self.path or self.path_index >= len(self.path):
            if now - self.path_update_timer >= self.path_update_interval:
                if self.last_goal_tile is None or player_tile != self.last_goal_tile:
                    self.path_update_timer = now
                    self.last_goal_tile = player_tile
                    walkables = self.game.map.get_walkable_tiles()

                    if self.ai_type == "melee":
                        goal_tile = self.get_melee_dest_tile(player_tile, walkables)
                    elif self.ai_type == "ranged":
                        goal_tile = self.get_ranged_dest_tile(player, player_tile, walkables)
                    else:
                        goal_tile = player_tile

                    if goal_tile:
                        self.path = self.game.pathfinder.find_path(self.get_current_tile(), goal_tile)
                        self.path_index = 0

        # At the very end of update()
        if self.pending_projectile:
            proj = self.pending_projectile
            self.pending_projectile = None
            return proj

        return None


    def decide_action(self, player, dist, dx, dy):
        current_tile = self.get_current_tile()
        player_tile = (
            int(player.center[0] // Config.TILE_SIZE),
            int(player.center[1] // Config.TILE_SIZE)
        )

        if self.ai_type == "melee":
            # Red zone (fixed 3x3)
            red_zone = [
                (player_tile[0] + dx, player_tile[1] + dy)
                for dx in range(-1, 2)
                for dy in range(-1, 2)
                if not (dx == 0 and dy == 0)
            ]
            if current_tile in red_zone and self.can_use_aoe():
                return self.use_aoe([player], self.center)

        elif self.ai_type == "ranged":
            ring_radius = Config.RANGED_RING_RADIUS
            yellow_ring = [
                (player_tile[0] + dx, player_tile[1] + dy)
                for dx in range(-ring_radius, ring_radius + 1)
                for dy in range(-ring_radius, ring_radius + 1)
                if abs(dx) == ring_radius or abs(dy) == ring_radius
            ]

            if current_tile in yellow_ring and self.can_use_projectile():
                wall_rects = self.game.map.get_wall_rects()
                if self.has_line_of_sight_from(self.center, player.center, wall_rects):
                    direction = (dx / dist, dy / dist) if dist != 0 else (0, 0)
                    return self.use_projectile(direction)
                else:
                    # LOS blocked, force repath
                    self.last_goal_tile = None

        return None

    def compute_path_to(self, player_pos):
        tile_size = Config.TILE_SIZE
        start_tile = (
            int(self.center[0] // tile_size),
            int(self.center[1] // tile_size)
        )
        goal_tile = (
            int(player_pos[0] // tile_size),
            int(player_pos[1] // tile_size)
        )

        path = self.game.pathfinder.find_path(start_tile, goal_tile)

        # ✅ Skip path if it goes back to last tile
        if path and len(path) >= 2 and path[1] == self.last_tile:
            path.pop(1)  # remove the bounce-back tile

        return path

    def get_current_tile(self):
        return (
            int(self.center[0] // Config.TILE_SIZE),
            int(self.center[1] // Config.TILE_SIZE)
        )

    def get_melee_dest_tile(self, player_tile, walkable_tiles):
        px, py = player_tile
        zone = [(px + dx, py + dy) for dx in range(-1, 2) for dy in range(-1, 2)]
        zone.remove(player_tile)
        return self._pick_closest_tile(zone, walkable_tiles)

    def get_ranged_dest_tile(self, player, player_tile, walkable_tiles, ring_radius=Config.RANGED_RING_RADIUS):
        px, py = player_tile
        zone = [
            (px + dx, py + dy)
            for dx in range(-ring_radius, ring_radius + 1)
            for dy in range(-ring_radius, ring_radius + 1)
            if abs(dx) == ring_radius or abs(dy) == ring_radius
        ]

        wall_rects = self.game.map.get_wall_rects()
        visible = []
        invisible = []

        for tile in zone:
            if tile not in walkable_tiles:
                continue
            tile_center = (
                tile[0] * Config.TILE_SIZE + Config.TILE_SIZE // 2,
                tile[1] * Config.TILE_SIZE + Config.TILE_SIZE // 2
            )
            if self.has_line_of_sight_from(tile_center, player.center, wall_rects):
                visible.append(tile)
            else:
                invisible.append(tile)

        if visible:
            return self._pick_closest_tile(visible, walkable_tiles)
        elif invisible:
            return self._pick_closest_tile(invisible, walkable_tiles)
        else:
            return None

    def _pick_closest_tile(self, candidates, walkable_tiles):
        valid = [tile for tile in candidates if tile in walkable_tiles]
        if not valid:
            return None
        return min(valid, key=lambda t: self._tile_dist(self.get_current_tile(), t))

    def _tile_dist(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def has_line_of_sight_from(self, from_pos, to_pos, wall_rects):
        for wall in wall_rects:
            if wall.clipline(from_pos, to_pos):
                return False
        return True

    def draw(self, surface, camera, color=(200, 50, 200)):
        x, y = camera.apply(self.position)
        rect = pg.Rect(int(x), int(y), self.size, self.size)

        # Draw filled rectangle
        pg.draw.rect(surface, self.health_color, rect)

    def draw_debug_path(self, surface, camera):
        if not self.path:
            return

        tile_size = Config.TILE_SIZE

        # Draw path tiles
        for i, (x, y) in enumerate(self.path):
            color = (150, 150, 255)  # blue
            if i == self.path_index:
                color = (255, 150, 150)  # red = current target
            elif i == len(self.path) - 1:
                color = (150, 255, 150)  # green = final goal

            screen_pos = camera.apply((x * tile_size, y * tile_size))
            rect = pg.Rect(screen_pos[0], screen_pos[1], tile_size, tile_size)
            pg.draw.rect(surface, color, rect, 2)  # thin outline box

    def draw_debug_los(self, surface, camera, target_pos, wall_rects):
        dx = target_pos[0] - self.center[0]
        dy = target_pos[1] - self.center[1]
        dist = math.hypot(dx, dy)

        if dist > Config.DETECTION_DISTANCE:
            return  # Too far, skip drawing

        start = camera.apply(self.center)
        end = camera.apply(target_pos)

        # Check LOS
        los_clear = True
        for wall in wall_rects:
            if wall.clipline(self.center, target_pos):
                los_clear = False
                break

        color = (0, 255, 0) if los_clear else (255, 0, 0)
        pg.draw.line(surface, color, start, end, 2)






