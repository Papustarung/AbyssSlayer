# AbyssSlayer

## Implemented Features for v0.5

### Core Systems
- **Map system**
  - Loads from image layout
  - Supports walls, chest zones, enemy zones
  - Exposes walkable tiles and spawn points
- **Camera system**
  - Keeps player centered on screen
  - All objects are offset based on camera position

---

### Player & Entity
- **Player movement**
  - 8-directional input
  - Diagonal movement normalized
  - Wall collision with `pygame.Rect`
- **Player state system**
  - States: `idle`, `moving`, `casting`, `dead`
  - Casting blocks movement
- **Entity base class**
  - Health, attack, defense, flat damage
  - Buff system (temporary + permanent)
  - Invincibility on damage
  - Scroll amplifier system

---

### Combat Mechanics
- **AOEAttack system**
  - Cast by player or entity
  - Applies damage to valid targets
  - Debug visualization (draws radius)
  - Supports multiple simultaneous AOEs with lifetime

---

### Buff System
- Buff amplifiers (permanent from scrolls)
- Temporary buffs (e.g. speed, damage)
- Cooldown and duration tracking
- Applied via `Buff` class, stored in `active_buffs`

---

### Scroll System
- `Scroll` class supports:
  - `projectile`, `aoe`, and `buff` types
  - Value randomized or set on spawn
  - Applies permanent upgrade to entities

---

### Game Management
- `GameManager` class
  - Manages stage loading, camera, player
  - Tracks multiple AOEs
- `Config` file
  - Centralized constants: screen size, flat damage, map paths

---

## Installation

1. Make sure Python 3 is installed.
2. Create a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows
    ```

3. Install required libraries:

    ```bash
    pip install -r requirements.txt
    ```

4. Run the game:

    ```bash
    python AbyssSlayer/abyss_game.py
    ```

