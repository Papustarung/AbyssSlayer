import time
from config import Config
from abyss_projectile import Projectile


class Entity:
    def __init__(self, base_health, base_attack, base_defense, spawn_point, size, stat_multiplier=1.0):
        self.team_id = "entity"
        # Stat
        self.health = base_health * stat_multiplier
        self.attack = base_attack * stat_multiplier
        self.defense = base_defense * stat_multiplier
        self.size = size
        self.speed = 5.0
        self.flat_damage = 1.0

        # Spawn location
        self.position = spawn_point

        # Buff
        self.amplifiers = {
            "projectile": 0,
            "aoe": 0,
            "buff": [0, 0]
        }
        self.active_buffs = {}

        # State
        self.state = "idle"
        self.invincible = False
        self.invincible_start = 0
        self.invincible_duration = 0.5

    def move(self, direction):
        dx, dy = direction
        self.position = (self.position[0] + dx * (self.speed + self.spd_buff),
                         self.position[1] + dy * (self.speed + self.spd_buff))

    def take_damage(self, dmg, attacker):
        if self.invincible:
            return

        flat_damage = 0
        if isinstance(attacker, Projectile):
            flat_damage = attacker.caster.flat_damage
        elif isinstance(attacker, Entity):
            flat_damage = attacker.flat_damage
        damage_taken = dmg * (dmg / (self.defense+dmg)) + flat_damage + Config.FLAT_DMG
        self.health -= damage_taken

        self.invincible = True
        self.invincible_start = time.time()

        if self.health <= 0:
            self.die()

    def die(self):
        self.state = "dead"
        print(f"{self.__class__.__name__} has been defeated!")

    def update(self):
        # Disable invincibility after duration
        if self.invincible and time.time() - self.invincible_start >= self.invincible_duration:
            self.invincible = False

    def is_visible(self):
        # Blinking effect
        if not self.invincible:
            return True
        return int((time.time() - self.invincible_start) * 10) % 2 == 0

    def apply_scroll_buff(self, scroll_type, value, buff):
        if scroll_type == "projectile":
            self.amplifiers["projectile"] += value
        elif scroll_type == "aoe":
            self.amplifiers["aoe"] += value
        elif scroll_type == "buff":
            self.amplifiers["buff"][0] += buff[0]
            self.amplifiers["buff"][1] += buff[1]