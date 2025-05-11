import random

class Scroll:
    def __init__(self, scroll_type: str, value: float = None):
        self.scroll_type = scroll_type
        self.value = value

        # Auto-generate value if not specified
        if self.value is None:
            if scroll_type == "projectile":
                self.value = 10
            elif scroll_type == "aoe":
                self.value = 4  # radius increase
            elif scroll_type == "buff":
                self.value = 1.0  # +1 sec to buff duration

    def apply(self, entity):
        print(f"Applying {self.scroll_type} to {entity}")
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


class ScrollGenerator:
    def __init__(self, total_chests):
        self.total_chests = total_chests
        self.generated_scrolls = []
        self.base_weights = {"projectile": 1.0, "aoe": 1.0, "buff": 1.0}
        self.scale_start = 5  # how many chests before scaling begins

    def generate_all_scrolls(self, get_player_scroll_count):
        for i in range(self.total_chests):
            if i < self.scale_start:
                scroll_type = self.weighted_random(self.base_weights)
            else:
                player_counts = get_player_scroll_count()
                scroll_type = self.scaled_random(player_counts)
            self.generated_scrolls.append(Scroll(scroll_type))

        return self.generated_scrolls

    def weighted_random(self, weights_dict):
        choices = list(weights_dict.keys())
        weights = list(weights_dict.values())
        return random.choices(choices, weights=weights, k=1)[0]

    def scaled_random(self, player_scroll_counts):
        # Invert player's scroll counts to give more of what they lack
        total = sum(player_scroll_counts.values()) + 1e-6
        inverse_weights = {
            key: (1.0 - (player_scroll_counts[key] / total)) + 0.1  # bias toward less frequent
            for key in self.base_weights
        }
        return self.weighted_random(inverse_weights)