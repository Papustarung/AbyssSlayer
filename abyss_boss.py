import random
from abyss_enemy import Enemy
from config import Config

class Boss(Enemy):
    def __init__(self, spawn_point, size, game_manager=None, stage_level=0):
        super().__init__(spawn_point, size, ai_type="ranged",
                         game_manager=game_manager, stage_level=stage_level)
        # (optionally) tune boss stats here
        self.health = 200 + 50 * stage_level
        self.max_health = self.health

        self.attack = 25 + 5 * stage_level

        self.decision_delay = 0.5  # faster reaction

        self.projectile_cooldown = 2.0
        self.projectile_radius = 8.0

        self.aoe_cooldown = 2.0
        self.base_radius = 64.0

        # phase tracking
        self.current_phase = 1
        self.phase2_entered = False
        self.phase3_entered = False

    def update(self, player):
        # 1) proximity swap
        bx, by = (int(self.center[0] // Config.TILE_SIZE),
                  int(self.center[1] // Config.TILE_SIZE))
        px, py = (int(player.center[0] // Config.TILE_SIZE),
                  int(player.center[1] // Config.TILE_SIZE))
        self.ai_type = "melee" if max(abs(bx - px), abs(by - py)) <= 3 else "ranged"

        # 2) phase check
        ratio = self.health / self.max_health
        if ratio <= 0.2 and not self.phase3_entered:
            self._enter_phase3()
        elif ratio <= 0.5 and not self.phase2_entered:
            self._enter_phase2()

        # 3) delegate movement + action
        return super().update(player)

    def _enter_phase2(self):
        self.phase2_entered = True
        self.current_phase = 2
        # buff: +1 speed
        self.speed += 1
        self.projectile_cast_time = 0.25

    def _enter_phase3(self):
        self.phase3_entered = True
        self.current_phase = 3
        # buff: +50% attack
        self.attack = int(self.attack * 1.5)
        # buff AOE radius
        self.base_radius += 8
        # buff projectile
        self.projectile_radius += 2
        self.projectile_speed += 3
        self.projectile_cooldown = 1.0
        self.projectile_cast_time = 0.0

    def decide_action(self, player, dist, dx, dy):
        # 0) compute normalized shot direction once
        if dist != 0:
            direction = (dx / dist, dy / dist)
        else:
            direction = (0, 0)

        # Phase 1
        if self.current_phase == 1:
            if self.ai_type == "melee" and self.can_use_aoe():
                return self.use_aoe([player], self.center)
            elif self.ai_type == "ranged" and self.can_use_projectile():
                return self.use_projectile(direction)

        # Phase 2
        elif self.current_phase in (2,3):
            if self.ai_type == "melee" and self.can_use_aoe():
                return self.use_aoe([player], self.center)
            elif self.ai_type == "ranged":
                # 50/50 projectile vs AOE at player.center
                if random.random() < 0.5 and self.can_use_projectile():
                    return self.use_projectile(direction)
                elif self.can_use_aoe():
                    return self.use_aoe([player], player.center)

        return None
