import time
import random
import math
import os
import pygame as pg
from collections import Counter
from config import Config  # assumes you’ve defined TILE_SIZE, SCREEN_WIDTH, MAP_LAYOUT
from abyss_map import Map  # your Map class with chest/enemy/walkable logic
from abyss_camera import Camera  # basic camera that applies offsets
from abyss_player import Player
from abyss_aoe_attack import AOEAttack
from abyss_projectile import Projectile
from abyss_enemy import Enemy
from pathfinder import AStarPathfinder
from abyss_scroll import ScrollGenerator
from abyss_chest import Chest
from interaction_system import InteractionSystem
from abyss_boss import Boss
from abyss_entity import Entity
from datalogger import DataLogger


class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.tile_size = Config.TILE_SIZE
        self.stage_keys = list(Config.MAP_LAYOUT.keys())  # e.g., ["stage 1", "stage 2", "stage 3"]
        self.current_stage_index = 0

        self.map = None
        self.camera = None
        self.enemies = []
        self.player = Player(spawn_point=(self.tile_size * 74, self.tile_size * 55), map_ref=self.map, game_manager=self)

        self.active_aoes = []
        self.projectiles = []

        self.load_stage(self.stage_keys[self.current_stage_index])

        self.game_over = False
        self.victory = False

        self.font = pg.font.SysFont(None, 32)  # big text (e.g. “Game Over”)
        self.smallfont = pg.font.SysFont(None, 24)  # smaller text (e.g. “Proj”, “AOE”, timers)

        os.makedirs("data", exist_ok=True)

        self.damage_logger = DataLogger(
            os.path.join("data", "damage_taken.csv"),
            fieldnames=["timestamp", "event", "phase", "details", "damage"]
        )

    def reset(self):
        """Restart the entire game from Stage 1."""
        # 1) Reset core flags
        self.current_stage_index = 0
        self.game_over = False
        self.victory = False

        # 2) Clear out lingering entities & effects
        self.enemies = []
        self.projectiles = []
        self.active_aoes = []
        self.chests = []

        # 3) Reload the first stage (which also respawns player)
        first_key = self.stage_keys[self.current_stage_index]
        self.load_stage(first_key)

    def load_stage(self, stage_key):
        self.player = Player(
            spawn_point=(self.tile_size * 74, self.tile_size * 55),
            map_ref=self.map,
            game_manager=self)
        map_path = Config.MAP_LAYOUT[stage_key]
        self.map = Map(map_path, self.tile_size)
        chest_spawns = self.map.chest_spawns

        # Generate scrolls
        scroll_generator = ScrollGenerator(len(chest_spawns))

        def get_player_scroll_count():
            return Counter({
                "projectile": self.player.scroll_counts["projectile"],
                "aoe": self.player.scroll_counts["aoe"],
                "buff": self.player.scroll_counts["buff"]
            })

        scrolls = scroll_generator.generate_all_scrolls(get_player_scroll_count)

        # Place chests with assigned scrolls
        self.chests = []
        for pos, scroll in zip(chest_spawns, scrolls):
            world_pos = (
                pos[0] * Config.TILE_SIZE,
                pos[1] * Config.TILE_SIZE
            )
            self.chests.append(Chest(world_pos, scroll))

        self.interaction_system = InteractionSystem(self.chests)

        self.boss_spawned = False
        self.boss = None
        self.boss_spawn_point = (320, 288)  # define special tile or use last enemy tile

        self.pathfinder = AStarPathfinder(self.map.grid)
        for spawn_cell in self.map.enemy_spawns:
            world_x = spawn_cell[0] * Config.TILE_SIZE
            world_y = spawn_cell[1] * Config.TILE_SIZE
            spawn_point = (world_x, world_y)

            ai_type = random.choice(["ranged", "melee"])
            enemy = Enemy(spawn_point=spawn_point, size=32, ai_type=ai_type, game_manager=self)


            # Optional: apply random scroll buff
            scroll_type = "projectile" if ai_type == "ranged" else "aoe"
            level = self.current_stage_index
            enemy.apply_scroll_buff(scroll_type, value=level * 5)

            self.enemies.append(enemy)

        self.camera = Camera(Config.GAME_SCREEN, Config.GAME_SCREEN)
        self.player = Player(spawn_point=(self.tile_size * 74, self.tile_size * 55), map_ref=self.map, game_manager=self)  # reset position

    def handle_win(self):
        self.game_over = True
        self.victory = True
        print("You win! 🎉")

    def handle_lose(self):
        self.game_over = True
        self.victory = False
        print("You lose… 💀")

    def advance_stage(self):
        self.current_stage_index += 1
        if self.current_stage_index < len(self.stage_keys):
            self.load_stage(self.stage_keys[self.current_stage_index])
        else:
            print("All stages completed.")

    def spawn_boss(self):
        self.boss_spawned = True
        self.boss = Boss(spawn_point=self.boss_spawn_point, size=Config.TILE_SIZE, game_manager=self, stage_level=self.current_stage_index)
        self.enemies.append(self.boss)
        print("Boss has spawned!")

    def update(self):
        result = self.player.update(self.enemies, self.camera)
        if isinstance(result, AOEAttack):
            self.active_aoes.append(result)
        elif isinstance(result, Projectile):
            self.projectiles.append(result)
        self.camera.update(self.player.center)

        self.interaction_system.update(self.player)

        dead_enemies = []
        for enemy in self.enemies:
            if enemy.state == "dead":
                dead_enemies.append(enemy)
                continue

            dx = enemy.center[0] - self.player.center[0]
            dy = enemy.center[1] - self.player.center[1]
            dist = (dx ** 2 + dy ** 2) ** 0.5

            if dist <= Config.DETECTION_DISTANCE:
                result = enemy.update(self.player)
                if isinstance(result, AOEAttack):
                    self.active_aoes.append(result)
                elif isinstance(result, Projectile):
                    self.projectiles.append(result)

        keys = pg.key.get_pressed()
        if keys[pg.K_j]:
            for en in self.enemies:
                if not isinstance(en, Boss):
                    en.die()

        # Check if boss should spawn
        if not self.boss_spawned and all(enemy.state == Entity.DEAD for enemy in self.enemies):
            self.spawn_boss()

        if self.boss_spawned and self.boss.state == Entity.DEAD:
            self.handle_win()
            return

            # 5) player death check: defeat
        if self.player.state == Entity.DEAD:
            self.handle_lose()
            return

        for p in self.projectiles:
            if p.caster.team_id == "player":
                p.update(self.map.get_wall_rects(), self.enemies)
            elif p.caster.team_id == "enemy":
                p.update(self.map.get_wall_rects(), [self.player])

        self.projectiles = [p for p in self.projectiles if p.active]

        for aoe in self.active_aoes:
            # Optional: expire based on lifetime or duration
            aoe.update()
            if hasattr(aoe, "start_time") and time.time() - aoe.start_time > aoe.lifetime:
                self.active_aoes.remove(aoe)

        self.active_aoes = [aoe for aoe in self.active_aoes if not aoe.is_expired()]

        for e in dead_enemies:
            self.enemies.remove(e)

    def draw(self):
        self.map.draw_placeholder(self.screen, self.camera, floor=True, chest=True, enemy=True)
        for aoe in self.active_aoes:
            aoe.draw(self.screen, self.camera)
        for p in self.projectiles:
            p.draw(self.screen, self.camera)
        for enemy in self.enemies:
            # enemy.draw_debug_path(self.screen, self.camera)
            enemy.draw(self.screen, self.camera)
            # enemy.draw_debug_los(self.screen, self.camera, self.player.center, self.map.get_wall_rects())

        if self.boss_spawned:
            self.boss.draw(self.screen, self.camera)

        self.map.draw_placeholder(self.screen, self.camera, wall=True)

        px, py = self.camera.apply(self.player.position)
        pg.draw.rect(self.screen, (0, 0, 255), (px, py, self.player.size, self.player.size))
        self.camera.draw_visibility_mask(self.screen, self.player.center, radius=Config.DETECTION_DISTANCE)
        self.camera.draw_visibility_mask(self.screen, self.player.center, radius=Config.DETECTION_DISTANCE - Config.FOG_LAYER_DISTANCE)
        self.camera.draw_visibility_mask(self.screen, self.player.center, radius=Config.DETECTION_DISTANCE - Config.FOG_LAYER_DISTANCE * 2)
        self.draw_state_label(self.screen)

        font = pg.font.SysFont(None, 20)

        for chest in self.chests:
            if not chest.opened and self.interaction_system._is_near(self.player, chest):
                screen_pos = self.camera.apply(chest.position)
                text_surf = font.render("Press F", True, (0, 150, 150))
                self.screen.blit(text_surf, (screen_pos[0], screen_pos[1] - 20))  # above chest

        self._draw_ability_buttons()
        if self.game_over:
            self._draw_end_screen()

    def draw_state_label(self, surface): # TEMP
        pg.font.init()
        font = pg.font.SysFont("arial", 30)
        state_text = f"State: {self.player.state}"
        stat_text = (f"Speed buff: {self.player.active_buffs.get("speed", {}).get("value", 0)} "
                     f"Dmg buff: {self.player.active_buffs.get("damage", {}).get("value", 0)}")


        proj = f"Projectile damage +{self.player.amplifiers["projectile"]}%"
        aoe =  f"AOE radius +{self.player.amplifiers["aoe"]}"
        buff = f"Buff duration {self.player.buff_max_duration} second"


        label = font.render(state_text, True, (255, 255, 255))  # white text
        label2 = font.render(stat_text, True, (255, 255, 255))  # white text


        pl = font.render(proj, True, (255, 255, 255))
        al = font.render(aoe, True, (255, 255, 255))
        bl = font.render(buff, True, (255, 255, 255))


        surface.blit(label, (Config.SCREEN_WIDTH - 390, Config.SCREEN_HEIGHT - 90))
        surface.blit(label2, (Config.SCREEN_WIDTH - 390, Config.SCREEN_HEIGHT - 180))  # 10px from left, 30px from bottom
        surface.blit(pl, (Config.SCREEN_WIDTH - 390, 90))
        surface.blit(al, (Config.SCREEN_WIDTH - 390, 180))
        surface.blit(bl, (Config.SCREEN_WIDTH - 390, 270))

    def _draw_ability_buttons(self):
        btn_size, padding = 48, 10
        start_x = padding
        start_y = Config.SCREEN_HEIGHT - btn_size - padding

        abilities = [
            ("Proj", self.player.can_use_projectile,
             self.player.projectile_last_used, self.player.projectile_cooldown),
            ("AOE", self.player.can_use_aoe,
             self.player.aoe_last_used, self.player.aoe_cooldown),
            ("Buff", self.player.can_use_buff,
             self.player.buff_last_used, self.player.buff_cooldown),
        ]
        now = pg.time.get_ticks() / 1000.0

        for idx, (label, can_use_fn, last_used, cooldown) in enumerate(abilities):
            x = start_x + idx * (btn_size + padding)
            y = start_y
            center = (x + btn_size // 2, y + btn_size // 2)
            radius = btn_size // 2 - 2  # leave room for ring

            # 1) draw button bg
            ready = can_use_fn()
            bg_color = (40, 40, 40) if not ready else (60, 60, 60)
            pg.draw.rect(self.screen, bg_color, (x, y, btn_size, btn_size), border_radius=6)

            # 2) label
            txt = self.smallfont.render(label, True, (255, 255, 255))
            txr = txt.get_rect(center=center)
            self.screen.blit(txt, txr)

            # 3) cooldown ring / ready ring
            if not ready:
                elapsed = now - last_used
                frac = max(0.0, min(1.0, elapsed / cooldown))
                # remaining fraction of cooldown
                rem = 1.0 - frac

                # draw a grey pie slice for the rem fraction
                segments = int(rem * 60)  # how many small triangles
                points = [center]
                for i in range(segments + 1):
                    angle = -math.pi / 2 + 2 * math.pi * (i / 60)
                    px = center[0] + math.cos(angle) * radius
                    py = center[1] + math.sin(angle) * radius
                    points.append((px, py))
                overlay = pg.Surface((btn_size, btn_size), pg.SRCALPHA)
                # shift points to local coords for the overlay surface
                local = [(px - x, py - y) for px, py in points]
                pg.draw.polygon(overlay, (0, 0, 0, 180), local)
                self.screen.blit(overlay, (x, y))

            else:
                # fully ready: draw a bright green ring
                pg.draw.circle(self.screen, (50, 200, 50), center, radius, width=3)

    def _draw_end_screen(self):
        # dark translucent backdrop
        overlay = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # main message
        msg_text = "YOU WIN!" if self.victory else "GAME OVER"
        msg_color = (50, 200, 50) if self.victory else (200, 50, 50)
        msg = self.font.render(msg_text, True, msg_color)
        msg_rect = msg.get_rect(center=(Config.SCREEN_WIDTH // 2,
                                        Config.SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(msg, msg_rect)

        # subtitle
        sub_text = "Press R to Restart" if self.victory else "Press Q to Quit"
        sub = self.smallfont.render(sub_text, True, (240, 240, 240))
        sub_rect = sub.get_rect(center=(Config.SCREEN_WIDTH // 2,
                                        Config.SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(sub, sub_rect)
