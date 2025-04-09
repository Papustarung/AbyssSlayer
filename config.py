

class Config:
    FLAT_DMG = 2.0
    SPRITES = {
        "player": {
            "idle": ["assets/player/idle1.png", "assets/player/idle2.png"],
            "walk": ["assets/player/walk1.png", "assets/player/walk2.png"],
            "projectile": ["assets/player/attack1.png", "assets/player/attack2.png"]
        },
        "enemy": {
            "idle": ["assets/enemy/idle1.png", "assets/enemy/idle2.png"],
            "walk": ["assets/enemy/walk1.png", "assets/enemy/walk2.png"]
        },
        "boss": {
            "idle": ["assets/boss/idle1.png"],
            "phase1": ["assets/boss/phase1_1.png", "assets/boss/phase1_2.png"]
        }
    }
