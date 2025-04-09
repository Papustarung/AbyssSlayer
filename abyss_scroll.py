class Scroll:
    def __init__(self, scroll_type, value, buff=(0, 0)):
        self.scroll_type = scroll_type  # "projectile", "aoe", or "buff"
        self.value = value
        self.buff = buff

    def apply(self, entity):
        entity.apply_scroll_buff(self.scroll_type, self.value, self.buff)