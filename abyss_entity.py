import time
import pygame as pg
from config import Config
from abyss_buff import Buff  # assuming Buff class is in buff.py
from abyss_aoe_attack import AOEAttack
from abyss_projectile import Projectile
from abyss_scroll import Scroll

class Entity:

    IDLE = "idle"
    MOVING = "moving"
    CASTING = "casting"
    DEAD = "dead"

    def __init__(self, base_health, base_attack, base_defense, spawn_point, size):
        self.team_id = "entity"

        # Stats
        self.health = base_health
        self.max_health = base_health
        self.attack = base_attack
        self.defense = base_defense
        self.size = size
        self.speed = 3.0
        self.flat_damage = 1.0
        self.position = spawn_point
        self.center = (
            self.position[0] + self.size / 2,
            self.position[1] + self.size / 2
        )

        self.scroll_counts = {
            "projectile": 0,
            "aoe": 0,
            "buff": 0
        }

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
        self.pending_action = None
        self.pending_projectile = None

        # Buff
        self.buff_cast_time = 1.5
        self.buff_cooldown = 15.0
        self.buff_last_used = -float("inf")

        # AOE
        self.base_radius = 48
        self.aoe_multiplier = 1.5
        self.aoe_cast_time = 1.0
        self.aoe_cooldown = 5.0
        self.aoe_last_used = -float("inf")
        self.target_pos = self.center

        # Projectile
        self.projectile_multiplier = 1.0
        self.projectile_cast_time = 0.5
        self.projectile_radius = 4.0
        self.projectile_speed = 6.0
        self.projectile_cooldown = 1.0
        self.projectile_last_used = -float("inf")

        # Invincibility
        self.invincible = False
        self.invincible_start = 0
        self.invincible_duration = 0.5

        self.health_color = (0, 255, 0)

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
        else:
            health_left = self.health/self.max_health
            red = int(255*(1-health_left))
            green = int(255*health_left)
            self.health_color = (red, green, 0)



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
        if self.state not in (Entity.IDLE, Entity.MOVING) or not self.can_use_buff():
            return

        def apply():
            Buff(self, "speed", 2.0, min(self.buff_max_duration, self.buff_cooldown)).apply()
            Buff(self, "damage", 5.0, min(self.buff_max_duration, self.buff_cooldown)).apply()
            self.buff_last_used = time.time()

        self.start_cast(self.buff_cast_time, apply)

    def use_aoe(self, targets, gen_pos):
        if self.state not in (Entity.IDLE, Entity.MOVING) or not self.can_use_aoe():
            return None

        # Create AOE for drawing
        aoe = AOEAttack(
            caster=self,
            generated_pos=gen_pos,
            base_radius=self.base_radius,
            multiplier=self.aoe_multiplier,
            target_type="enemy" if self.team_id == "player" else "player"
        )

        def apply_aoe_damage():
            aoe.apply_to_targets(targets)
            self.aoe_last_used = time.time()

        self.start_cast(self.aoe_cast_time, on_complete=apply_aoe_damage)
        return aoe

    def use_projectile(self, direction):
        if self.state not in (Entity.IDLE, Entity.MOVING) or not self.can_use_projectile():
            return None

        def launch():
            projectile = Projectile(
                caster=self,
                position=self.center,
                direction=direction,
                radius=self.projectile_radius,
                speed=self.projectile_speed,
                base_damage=self.attack
            )
            self.projectile_last_used = time.time()
            self.pending_projectile = projectile

        self.start_cast(self.projectile_cast_time, on_complete=launch)
        return None

    def can_use_aoe(self):
        return time.time() - self.aoe_last_used >= self.aoe_cooldown

    def can_use_projectile(self):
        return time.time() - self.projectile_last_used >= self.projectile_cooldown

    def can_use_buff(self):
        return time.time() - self.buff_last_used >= self.buff_cooldown

    def apply_scroll_buff(self, scroll_type, value):
        if scroll_type == "projectile":
            self.amplifiers["projectile"] += value
        elif scroll_type == "aoe":
            self.amplifiers["aoe"] += value
        elif scroll_type == "buff":
            self.buff_max_duration += value

    def obtain_scroll(self, scroll: Scroll):
        print(f"Obtaining scroll: {scroll.scroll_type}")
        if not hasattr(self, "scroll_counts"):
            self.scroll_counts = {"projectile": 0, "aoe": 0, "buff": 0}

        scroll_type = scroll.scroll_type
        self.scroll_counts[scroll_type] += 1
        scroll.apply(self)  # internally applies the buff
        print(f"Obtained: {scroll.get_description()}")

    def start_cast(self, duration, on_complete=None):
        self.state = Entity.CASTING
        self.cast_start_time = time.time()
        self.cast_duration = duration
        self.pending_action = on_complete  # Store action to run later

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
            if self.pending_action:
                self.pending_action()  # Call the function
                self.pending_action = None

        if self.state not in (Entity.CASTING, Entity.MOVING, Entity.DEAD):
            self.state = Entity.IDLE

        # Invincibility
        if self.invincible and current_time - self.invincible_start >= self.invincible_duration:
            self.invincible = False

    def is_visible(self):
        if not self.invincible:
            return True
        return int((time.time() - self.invincible_start) * 10) % 2 == 0

    def get_rect(self):
        return pg.Rect(self.position[0], self.position[1], self.size, self.size)