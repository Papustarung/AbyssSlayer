# **Abyss Slayer**

1. ### **Project Overview**

This project is a 2D dungeon adventure game, drawing inspiration from various dungeon crawlers, roguelikes, and action RPGs. The game focuses on strategic combat, looting mechanics, and adaptive difficulty scaling. Players explore procedurally generated dungeons, engage in combat, and enhance their abilities through a structured looting system. Players must navigate through three dungeon stages, each ending with a boss fight that increases in difficulty through adaptive attack probability and special moveset activation.

2. **Project Review**

Reference Games: Dungeon Crawlers & Roguelikes

This game builds upon mechanics found in dungeon crawlers and roguelike games while introducing distinct improvements:

* **Predefined abilities**: Instead of random weapons, players start with three core abilities: *Projectile Attack*, *AOE Damage*, and *Temporary Buffs*.  
* **Stackable Ability System**: Players enhance abilities by collecting *scrolls* instead of acquiring new weapons.  
* **Dynamic Boss AI**: A single boss enemy is used across all three stages but becomes stronger and more complex through probability-based move adjustments.

3. **Programming Development**

**3.1 Game Concept**  
The game features a dungeon-crawling combat system where players explore interconnected rooms filled with enemies, loot, and environmental challenges.

* **Player Abilities & Progression**:  
  * Players begin with **three core abilities**:  
    1. **Projectile Attack** – Shoots a ranged attack in the aimed direction.  
    2. **AOE Damage** – Deals area-based damage centered on the player.  
    3. **Temporary Buffs** – Grants boosts like increased speed or damage for a limited time.  
  * Abilities are **enhanced by collecting scrolls**, which increase effectiveness rather than introducing new skills.  
* **Combat System**:  
  * Players and enemies can both deal and receive damage upon contact.  
  * **Temporary invincibility** is granted after attacking to prevent instant counterattacks.  
* **Looting System**:  
  * All loot is pre-generated at the start of the game to ensure fair distribution and predictable balancing.  
  * Chests randomly spawn at four (maybe more) predefined locations per stage.  
  * Each chest contains a **scroll** that enhances one of the three abilities.  
  * The loot drop system determines scroll rewards using a **hybrid approach**:  
1. **Weighted Random Selection** – Ensures randomness and unpredictability, providing unique experiences in every playthrough.  
2. **Dynamic Probability Scaling** – Activates after a few loot drops, adjusting drop rates based on the player's inventory. This ensures a well-rounded power progression while preserving early-game randomness and excitement.  
   *   
* **Boss Battles**:  
  * The **same boss appears in each stage**, but its **attack probability and special moves change** as the game progresses.  
  * The boss uses a **real-time adaptive AI system**, adjusting its moveset dynamically based on the player's behavior and stage difficulty  
  * At **50% and 20% health**, the boss gains **new abilities and enhanced attack patterns**, adapting its attack choices rather than following a pre-generated sequence.  
  * Boss moves are selected using:  
    1. **Weighted Probability** – Each attack has a predefined base chance of occurring.  
    2. **Adaptive AI Decision Making** – The boss reacts dynamically to the player's actions, increasing the likelihood of counterattacks or strategic shifts based on real-time inputs.  
       Example ideas:  
- Projectile spam → Boss speeds up, gains ranged counters, or armor.  
- Slow play (low DPS) → Boss speeds up, gains healing, or forces engagements.  
  3. **Markov Chain Transitions (I found this method interesting)** – Ensures that the boss does not repeat the same move too frequently, leading to varied combat experiences.

**3.2  Object-Oriented Programming Implementation**

**(\*\*\*\*\*SUBJECT TO CHANGE\*\*\*\*\*)**

#### **Player(Entity)**

* Controls player input, movement, and ability usage.  
* Tracks state (idle, moving, casting) in real-time.  
* Handles collision and ability cooldowns.  
* Can trigger Projectile, AOEAttack, or Buff.

#### **Enemy(Entity)**

* Uses basic AI (pathfinding and targeting player).  
* Can cast abilities like AOE similar to Player.  
* Will later include behavior adjustments by type (melee, ranged, elite).

#### **Boss(Enemy)**

* Adaptive AI: modifies its move probabilities based on:  
  * Stage level  
  * Player behavior (e.g., spamming projectiles)  
  * Health thresholds (50%, 20%)  
* Supports phase transitions and move variation (e.g., via Markov Chain logic).  
* Uses the same ability system as enemies but with enhanced decision-making.

#### **Projectile**

* Represents a moving, directional attack (e.g., fireball).  
* Has a caster, speed, direction, and damage.  
* Will use CollisionManager to detect and apply damage.

#### **AOEAttack**

* Area-of-effect skill centered at a point (Entity.center).  
* Can be used by any Entity, including boss/enemies.  
* Supports debug visualization (draw()), auto-expiration.

#### **Buff**

* Temporarily boosts attributes like speed or flat damage.  
* Activated by calling Buff(caster, type, value, duration).apply()  
* Internally updates the entity’s active\_buffs dictionary.

#### **Scroll**

* Represents permanent upgrade from loot.  
* Types: "projectile", "aoe", "buff"  
* Applied using scroll.apply(entity)  
  * Projectile scroll → \+damage amplifier  
  * AOE scroll → \+radius  
  * Buff scroll → \+max duration

#### **Chest**

* Spawns at predefined locations on the map.  
* Drops one random scroll when opened.  
* Uses dynamic probability based on player’s scroll inventory.

#### **Map**

* Loads from image to define:  
  * Wall tiles  
  * Enemy spawn zones  
  * Chest spawn zones  
* Exposes methods:  
  * is\_walkable(x, y)  
  * get\_wall\_rects()  
  * draw\_placeholder()

#### **GameManager**

* Controls game flow, including:  
  * Loading maps  
  * Tracking Player, Enemy, and AOEAttack instances  
* Updates camera to center on player.  
* Manages active\_aoes\[\] list for rendering all AOE debug circles.

#### **Camera**

* Keeps player centered in the viewport.  
* Applies position offset to all world objects using apply(world\_pos).

#### **UIManager**

* Manages HUD elements like:  
  * Health bars  
  * Cooldown indicators  
  * Interaction prompts (Press F to open chest)  
* Can render real-time state display (State: idle, etc.)

UML Diagram (better version of implementation): [Lucidchart document](https://lucid.app/lucidchart/3fca8dda-2916-4b5a-9cee-d1ecb6da0fad/edit?viewport_loc=-8272%2C-2463%2C5700%2C2621%2C0_0&invitationId=inv_58fec87f-98cf-420b-b49b-346c0a72d58b)

**3.3 Algorithms Involved**  
The game utilizes several algorithms to improve mechanics and performance:

* **Hybrid Loot Drop System** **\-** Uses weighted random selection early and dynamic probability scaling later.  
* **Markov Chain Decision-Making** \- Prevents repetitive attack patterns for bosses.  
  \> [Markov chains](https://medium.com/my-games-company/advanced-math-in-game-design-random-walks-and-markovian-chains-in-action-b12d3749d922) \<  
* **Real-Time Adaptive AI** \- Allows the boss to react dynamically based on player behavior.  
* **A\* Pathfinding** \- Enables enemies to navigate towards the player while avoiding obstacles.  
  [Easy Pathfinding for Unity 2D and 3D Games\! \[Pathfinding Tutorial\]](https://youtu.be/UHnOW-OimLQ?si=YQ05yJcGnNX3F-cG)  
* **Collision Detection** \- Manages player and enemy interactions.  
* **AI Behavior Systems** \- Governs enemy attack decisions and movement patterns.

4. **Statistical Data (Prop Stats)**

**4.1 Data Features**

* **Player movement distance** – Tracks how far a player moves per stage.  
* **Attack accuracy** – Measures hit vs. miss ratio for projectiles and melee attacks.  
* **Stage completion time** – Records how long it takes players to clear a level.  
* **Boss move frequency and adaptation rate** – Monitors the boss's reaction to player behavior.  
* **Loot drop distribution** – Logs the types and frequency of looted scrolls.

**4.2 Data Recording Method**

The game will store statistical data using:

* **CSV files**  
* **JSON storage**

**4.3 Data Analysis Report**

### **Table 1\. Data Feature Collection Details**

| Feature | Why It is Good to Have This Data? (What Can It Be Used For?) | How Will I Obtain 50 Values of This Feature Data? | Which Variable (and Class) Will You Collect This From? | How Will I Display This Feature Data? (Summary/Statistics or Graph) |
| ----- | ----- | ----- | ----- | ----- |
| Damage Taken per Hit | Evaluates combat difficulty and player survivability by showing variation in damage received. | Record each damage value every time the player is hit during gameplay (across multiple sessions). | damage\_amount from the Player.take\_damage() method. | Summary statistics (e.g., average, min, max, SD) in the table; distribution graph (boxplot/histogram) to show spread. |
| Distance Moved per Room | Reveals player behavior (cautious exploration vs. rushing) and informs level pacing and design analysis. | Log the movement distance for each room transition (each room yields one value; 50+ rooms collected over sessions). | Calculated as position\_delta in Player.update() or tracked by the GameManager during room transitions. | Summary statistics (e.g., average, min, max) and a line graph (time-series) or histogram displaying distances per room. |
| Player Movement Heat Map | Provides a spatial overview of where players spend the most time, helping identify hotspots, bottlenecks, and key engagement areas within the dungeon. | Continuously record the player's (x, y) coordinates at regular intervals and aggregate these into grid cell counts over sessions. | Player position (x, y) from Player.update() or from a dedicated tracking module in GameManager. | Heat map overlay on the dungeon layout. |
| Buff Type Preference | Indicates strategic tendencies by revealing whether players favor speed buffs or damage buffs, which is critical for balancing ability impacts. | Log each buff activation event with its specific type (one value per cast; 50+ events accumulated across sessions). | buff\_type from the Player.use\_buff() method. | Displayed as a pie chart showing the proportion of each buff type; summary counts/percentages may also be presented in a table. |
| Enemy Encounter Duration | Measures how long players remain engaged in combat per room, providing insight into encounter intensity and pacing without merely counting enemies. | Record the start and end times of enemy encounters in each room and calculate the duration for each (50+ values across sessions). | Encounter timestamps (encounter\_start\_time and encounter\_end\_time) in the Room class or GameManager. | Summary statistics (e.g., average, SD, median) in a table; distribution graph (histogram or line graph) to show encounter durations. |
| Scroll Type Collected | Tracks loot balance and fairness by recording the distribution of scroll types collected, which informs ability progression and RNG tuning. | Log each scroll collection event (one value per event; 50+ collection events over sessions). | scroll\_type from the Scroll.apply\_to\_player() method. | Displayed as a stacked bar chart or stacked area graph showing frequency over time, with summary counts also available. |

**Table 2\. Data Display Plan for Proposal \#4**

#### **4.3.1 Table Display: Summary Statistics**

**(A) Features for the Table:**

* Damage Taken per Hit  
* Distance Moved per Room  
* Enemy Encounter Duration

**(B) Statistical Values to Present:**

* Damage Taken per Hit: Average, Minimum, Maximum, Standard Deviation (SD)  
* Distance Moved per Room: Average, Minimum, Maximum  
* Enemy Encounter Duration: Average, Standard Deviation, Median (or a chosen percentile)

#### **4.3.2 Graph Display: Visualizing Key Features**

| Graph \# | Feature | Graph Type | Graph Objective | X-axis | Y-axis |
| ----- | ----- | ----- | ----- | ----- | ----- |
| **1** | Damage Taken per Hit | Boxplot or Histogram | Display the distribution of damage values to evaluate combat difficulty, variability, and outliers. | Hit Index or Session | Damage Value (HP lost) |
| **2** | Buff Type Preference | Pie Chart | Show the proportion of each buff type used to reveal player strategic preferences (e.g., speed vs. damage). | *(Not applicable for pie charts)* | Proportion (% usage per buff type) |
| **3** | Distance Moved per Room | Line Graph | Illustrate trends in player movement across rooms to assess exploration patterns and identify pacing issues. | Room Number (sequential order) | Distance Moved (game units) |

Each graph is designed to address a specific gameplay aspect:

* **Graph 1:** Helps in understanding combat intensity and identifying any damage spikes or balance issues.

* **Graph 2:** Provides insights into how players utilize their buffs, indicating overall strategy.

* **Graph 3:** Offers a view into player movement behavior over time, which can inform level design and pacing improvements.

**5\. Project Timeline**

| Week | Task |
| :---- | :---- |
| 1 (10 March) | Proposal submission / Project initiation |
| 2 (17 March) | Full proposal submission |
| 3 (24 March) | Set up project structure, implement basic player movement and UI |
| 4 (31 March) | Develop core combat mechanics |
| 5 (7 April) | Implement enemy AI and looting system |
| 6 (14 April) | Submission week (Draft) |

**Checkpoint:**

* 16 Apr: 50% Basic game elements and some combat abilities  
* 23 Apr: 75% Complete the game  
* 11 May: 100% Complete the project (including data collection)

**6\. Document version**  
Version: *4.0*  
Date: *31 March 2025*

[Github](https://github.com/Papustarung/AbyssSlayer)