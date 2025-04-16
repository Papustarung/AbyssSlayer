import time
from config import Config
from abyss_buff import Buff  # assuming Buff class is in buff.py
from abyss_aoe_attack import AOEAttack

class Entity:

    IDLE = "idle"
    MOVING = "moving"
    CASTING = "casting"
    DEAD = "dead"

    def __init__(self, base_health, base_attack, base_defense, spawn_point, size, stat_multiplier=1.0):
        self.team_id = "entity"

        # Stats
        self.health = base_health * stat_multiplier
        self.attack = base_attack * stat_multiplier
        self.defense = base_defense * stat_multiplier
        self.size = size
        self.speed = 5.0
        self.flat_damage = 1.0
        self.position = spawn_point
        self.center = (
            self.position[0] + self.size / 2,
            self.position[1] + self.size / 2
        )

        # Amplifiers
        self.amplifiers = {
            "projectile": 0,
            "aoe": 0
        }
        self.buff_max_duration = 5.0

        # Buffs
        self.active_buffs = {}

        # State
        self.state = Entity.IDLE
        self.cast_start_time = 0
        self.cast_duration = 0

        # AOE cooldown
        self.aoe_cooldown = 4.0
        self.aoe_last_used = -float("inf")

        # Invincibility
        self.invincible = False
        self.invincible_start = 0
        self.invincible_duration = 0.5

    def update_center(self):
        self.center = (
            self.position[0] + self.size / 2,
            self.position[1] + self.size / 2
        )

    def move(self, direction):
        if self.state in (Entity.CASTING, Entity.DEAD):
            return

        dx, dy = direction
        if dx != 0 and dy != 0:
            scale = 1 / (2 ** 0.5)
            dx *= scale
            dy *= scale

        speed_boost = self.active_buffs.get("speed", {}).get("value", 0)
        total_speed = self.speed + speed_boost
        self.position = (
            self.position[0] + dx * total_speed,
            self.position[1] + dy * total_speed
        )
        self.update_center()

        if dx != 0 or dy != 0:
            self.state = Entity.MOVING

    def take_damage(self, dmg, attacker):
        if self.invincible or self.state == Entity.DEAD:
            return

        flat_damage = getattr(attacker, "flat_damage", 0)
        buff_bonus = attacker.active_buffs.get("damage", {}).get("value", 0)
        total_flat = flat_damage + buff_bonus + Config.FLAT_DMG

        damage_taken = dmg * (dmg / (self.defense + dmg)) + total_flat
        self.health -= damage_taken

        self.invincible = True
        self.invincible_start = time.time()

        if self.health <= 0:
            self.die()

    def die(self):
        self.state = Entity.DEAD
        print(f"{self.__class__.__name__} has been defeated!")

    def apply_temporary_buff(self, buff_type, value, duration):
        self.active_buffs[buff_type] = {
            "value": value,
            "start_time": time.time(),
            "duration": duration
        }

    def use_buff(self):
        if self.state != Entity.IDLE:
            return
        Buff(self, "speed", 2.0, self.buff_max_duration).apply()
        Buff(self, "damage", 3.0, self.buff_max_duration).apply()
        self.start_cast(Entity.CASTING, 1)

    def use_aoe(self, targets, base_radius=48, multiplier=1.0, cast_time=1):
        if not self.can_use_aoe():
            return None

        aoe = AOEAttack(
            caster=self,
            generated_pos=self.center,
            base_radius=base_radius,
            multiplier=multiplier,
            target_type="enemy" if self.team_id == "player" else "player"
        )
        aoe.apply_to_targets(targets)
        self.aoe_last_used = time.time()
        self.start_cast(Entity.CASTING, cast_time)
        return aoe

    def can_use_aoe(self):
        return time.time() - self.aoe_last_used >= self.aoe_cooldown

    def apply_scroll_buff(self, scroll_type, value, buff=None):
        if scroll_type == "projectile":
            self.amplifiers["projectile"] += value
        elif scroll_type == "aoe":
            self.amplifiers["aoe"] += value
        elif scroll_type == "buff":
            self.buff_max_duration += value

    def start_cast(self, state, duration):
        self.state = state
        self.cast_start_time = time.time()
        self.cast_duration = duration

    def update(self, **kwargs):
        current_time = time.time()

        # Buff expiration
        expired = [b for b, v in self.active_buffs.items()
                   if current_time - v["start_time"] >= v["duration"]]
        for b in expired:
            del self.active_buffs[b]

        # Cast recovery
        if self.state == Entity.CASTING and current_time - self.cast_start_time >= self.cast_duration:
            self.state = Entity.IDLE

        if self.state not in (Entity.CASTING, Entity.MOVING, Entity.DEAD):
            self.state = Entity.IDLE

        # Invincibility
        if self.invincible and current_time - self.invincible_start >= self.invincible_duration:
            self.invincible = False

    def is_visible(self):
        if not self.invincible:
            return True
        return int((time.time() - self.invincible_start) * 10) % 2 == 0