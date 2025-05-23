**# Abyss Slayer**

A 2D soul-knight-inspired dungeon crawler built in Pygame. Explore, loot, and fight an adaptive boss!

---

### Core Systems

* **Map from Image**

  * Parse PNG layouts (walls, floor, chest-spawn, enemy-spawn) into a tile grid
  * Auto-extract walkable tiles + spawn points
* **Camera**

  * Smooth follow with world→screen coordinate transforms
  * Applies to all draw calls

---

### Player & Entities

* **Player**

  * 8-directional, normalized diagonal movement + tile collision
  * State machine: `IDLE`, `MOVING`, `CASTING`, `DEAD`
  * One-action-at-a-time: casting or moving
  * Invincibility frames on hit
* **Entity Base**

  * HP, attack, defense, flat-damage stats
  * Permanent scroll amplifiers + temporary Buffs
  * `use_projectile(direction)` + `use_aoe(targets, target_pos)` APIs

---

### Combat & Boss AI

* **Projectiles**

  * Directional shooting with per-shot radius & speed
  * Line-of-sight check + cooldown
* **AOE Attacks**

  * Centered on caster or target position
  * Radius = `base_radius × aoe_multiplier`
  * Multiple simultaneous AOEs with lifetimes
* **Boss Phases**

  * **Phase 1 (>50% HP)**:

    * Melee → self-center AOE
    * Ranged → projectile only
  * **Phase 2 (20–50% HP)**:

    * On enter: `speed += 1`
    * Ranged → 50/50 split between projectile & player-center AOE
  * **Phase 3 (≤20% HP)**:

    * On enter: `attack ×=1.5`, `aoe_multiplier +=0.5`, `proj_radius +=2`, `proj_speed +=2`
    * Ranged → fires both buffed projectile and targeted AOE
* **AI Pattern**

  * Tile-based “melee ring” vs “ranged ring” switching
  * Optional Markov-chain attack sequencing

---

### Buffs & Scrolls

* **Buff System**

  * Temporary buffs (speed, flat damage) managed in `active_buffs`
  * Cooldown/duration tracked per-Buff
* **Scrolls**

  * Types: `projectile`, `aoe`, `buff`
  * Randomized values at chest spawn
  * Permanently amplify entity stats

---

### Game Management & UI

* **GameManager**

  * One `update()` / `draw()` facade for game loop
  * Stage loading, entity/aoe spawn, win/lose checks
  * `reset()` to restart from Stage 1
* **UI Overlays**

  * Health bars for player & boss
  * Stage indicator
  * **Ability buttons** (Proj / AOE / Buff) at bottom-left

    * Gray out when on cooldown via `can_use_*()`
    * Radial cooldown ring + remaining-seconds text
  * End screens: “YOU WIN!” or “GAME OVER” with translucent backdrop

---


## ▶ How to Play

**Movement:** Use WASD to move in 8 directions (diagonals auto-normalize).

**Abilities:**

* **Projectile (key: E)**: Fires a directional shot toward the cursor or last movement direction.
* **AOE Blast (key: R)**: Creates an area‑of‑effect explosion at your position or, in later phases, at the target.
* **Buff (key: Q)**: Grants a temporary speed and damage boost.

Cooldown is shown on the bottom‑left buttons (gray if unavailable).

**Looting:** Stand on the yellow tiles and press F to obtain scroll.


**Goal:** Clear all enemies in each room to spawn the boss, then defeat the boss through all its adaptive phases (melee and ranged patterns) to win the run.

## 💻 Installation & Running

1. **Clone & enter** the repo:

   ```bash
   git clone <your-repo-url> && cd AbyssSlayer
   ```
2. **(Optional)** Create and activate a venv:

   ```bash
   python3 -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate.bat     # Windows
   ```
3. **Install** dependencies:

   ```bash
   pip install -r requirements.txt
   ```
4. **Run** the game:

   ```bash
   python abyss_game.py
   ```

---

Enjoy experimenting with boss phases, scroll builds, and your own balance tweaks!
