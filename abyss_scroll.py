import random

class Scroll:
    def __init__(self, scroll_type: str, value: float = None, buff=None):
        self.scroll_type = scroll_type
        self.value = value

        # Auto-generate value if not specified
        if self.value is None:
            if scroll_type == "projectile":
                self.value = random.randint(5, 7)  # +5~7 projectile dmg
            elif scroll_type == "aoe":
                self.value = 2  # radius increase
            elif scroll_type == "buff":
                self.value = 1.0  # +1 sec to buff duration

    def apply(self, entity):
        entity.apply_scroll_buff(
            self.scroll_type,
            self.value,
        )

    def get_description(self):
        if self.scroll_type == "projectile":
            return f"Projectile Scroll: +{self.value} projectile damage"
        elif self.scroll_type == "aoe":
            return f"AOE Scroll: +{self.value} AOE radius"
        elif self.scroll_type == "buff":
            return f"Buff Scroll: +{self.value} sec buff duration"
        else:
            return "Unknown Scroll"
