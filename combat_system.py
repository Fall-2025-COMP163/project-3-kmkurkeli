# AI Usage - AI assisted with explanations, debugging, code structure, and implementation guidance.
"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Starter Code

Name: [Kurkeli Kurkeli]

AI Usage: [Helped with debugging, structuring my code and explanations.]

Handles combat mechanics
"""
import random

from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError
)

from character_manager import gain_experience, add_gold


# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================

def create_enemy(enemy_type):
    """
    Create an enemy based on type

    Example enemy types and stats:
    - goblin: health=50, strength=8, magic=2, xp_reward=25, gold_reward=10
    - orc: health=80, strength=12, magic=5, xp_reward=50, gold_reward=25
    - dragon: health=200, strength=25, magic=15, xp_reward=200, gold_reward=100

    Returns: Enemy dictionary
    Raises: InvalidTargetError if enemy_type not recognized
    """
    enemy_type = enemy_type.lower()

    if enemy_type == "goblin":
        enemy = {
            "name": "Goblin",
            "health": 50,
            "max_health": 50,
            "strength": 8,
            "magic": 2,
            "xp_reward": 25,
            "gold_reward": 10
        }
    elif enemy_type == "orc":
        enemy = {
            "name": "Orc",
            "health": 80,
            "max_health": 80,
            "strength": 12,
            "magic": 5,
            "xp_reward": 50,
            "gold_reward": 25
        }
    elif enemy_type == "dragon":
        enemy = {
            "name": "Dragon",
            "health": 200,
            "max_health": 200,
            "strength": 25,
            "magic": 15,
            "xp_reward": 200,
            "gold_reward": 100
        }
    else:
        raise InvalidTargetError(f"Unknown enemy type: {enemy_type}")

    return enemy


def get_random_enemy_for_level(character_level):
    """
    Get an appropriate enemy for character's level

    Level 1-2: Goblins
    Level 3-5: Orcs
    Level 6+: Dragons

    Returns: Enemy dictionary
    """
    if character_level <= 2:
        enemy_type = "goblin"
    elif character_level <= 5:
        enemy_type = "orc"
    else:
        enemy_type = "dragon"

    return create_enemy(enemy_type)


# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class SimpleBattle:
    """
    Simple turn-based combat system

    Manages combat between character and enemy
    """

    def __init__(self, character, enemy):
        """Initialize battle with character and enemy"""
        self.character = character
        self.enemy = enemy
        self.combat_active = True
        self.turn_counter = 1

        # Track that this character is in battle
        self.character.setdefault("in_battle", False)
        self.character["in_battle"] = True

        # Reset ability cooldown flag for this battle
        self.character["ability_on_cooldown"] = False

    def start_battle(self):
        """
        Start the combat loop

        Returns: Dictionary with battle results:
                {'winner': 'player'|'enemy', 'xp_gained': int, 'gold_gained': int}

        Raises: CharacterDeadError if character is already dead
        """
        if self.character.get("health", 0) <= 0:
            raise CharacterDeadError("Character is already dead and cannot fight.")

        display_battle_log("Battle begins!")
        display_combat_stats(self.character, self.enemy)

        while self.combat_active:
            # Player goes first
            self.player_turn()
            winner = self.check_battle_end()
            if winner is not None:
                break

            # Enemy turn
            self.enemy_turn()
            winner = self.check_battle_end()
            if winner is not None:
                break

            self.turn_counter += 1

        # Battle ended – mark character as no longer in battle
        self.combat_active = False
        self.character["in_battle"] = False

        if winner == "player":
            rewards = get_victory_rewards(self.enemy)
            xp = rewards["xp"]
            gold = rewards["gold"]

            # Apply rewards using character_manager functions
            gain_experience(self.character, xp)
            add_gold(self.character, gold)

            display_battle_log(
                f"You defeated {self.enemy['name']}! "
                f"Gained {xp} XP and {gold} gold."
            )

            return {
                "winner": "player",
                "xp_gained": xp,
                "gold_gained": gold
            }
        else:
            display_battle_log("You were defeated...")
            return {
                "winner": "enemy",
                "xp_gained": 0,
                "gold_gained": 0
            }

    def player_turn(self):
        """
        Handle player's turn

        Displays options:
        1. Basic Attack
        2. Special Ability (if available)
        3. Try to Run

        Raises: CombatNotActiveError if called outside of battle
        """
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not active.")

        # For automated testing / simple gameplay:
        # Default action: basic attack
        damage = self.calculate_damage(self.character, self.enemy)
        self.apply_damage(self.enemy, damage)
        display_battle_log(
            f"{self.character.get('name', 'Hero')} attacks "
            f"{self.enemy['name']} for {damage} damage!"
        )
        display_combat_stats(self.character, self.enemy)

    def enemy_turn(self):
        """
        Handle enemy's turn - simple AI

        Enemy always attacks

        Raises: CombatNotActiveError if called outside of battle
        """
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not active.")

        damage = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, damage)
        display_battle_log(
            f"{self.enemy['name']} attacks "
            f"{self.character.get('name', 'Hero')} for {damage} damage!"
        )
        display_combat_stats(self.character, self.enemy)

    def calculate_damage(self, attacker, defender):
        """
        Calculate damage from attack

        Damage formula: attacker['strength'] - (defender['strength'] // 4)
        Minimum damage: 1

        Returns: Integer damage amount
        """
        atk = attacker.get("strength", 0)
        defense = defender.get("strength", 0) // 4
        damage = atk - defense
        if damage < 1:
            damage = 1
        return damage

    def apply_damage(self, target, damage):
        """
        Apply damage to a character or enemy

        Reduces health, prevents negative health
        """
        target["health"] = max(0, target.get("health", 0) - damage)

    def check_battle_end(self):
        """
        Check if battle is over

        Returns: 'player' if enemy dead, 'enemy' if character dead, None if ongoing
        """
        if self.enemy.get("health", 0) <= 0:
            self.combat_active = False
            self.character["in_battle"] = False
            return "player"
        if self.character.get("health", 0) <= 0:
            self.combat_active = False
            self.character["in_battle"] = False
            return "enemy"
        return None

    def attempt_escape(self):
        """
        Try to escape from battle

        50% success chance

        Returns: True if escaped, False if failed
        """
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not active.")

        success = random.random() < 0.5
        if success:
            display_battle_log("You successfully escaped from battle!")
            self.combat_active = False
            self.character["in_battle"] = False
        else:
            display_battle_log("Escape attempt failed!")

        return success


# ============================================================================
# SPECIAL ABILITIES
# ============================================================================

def use_special_ability(character, enemy):
    """
    Use character's class-specific special ability

    Example abilities by class:
    - Warrior: Power Strike (2x strength damage)
    - Mage: Fireball (2x magic damage)
    - Rogue: Critical Strike (3x strength damage, 50% chance)
    - Cleric: Heal (restore 30 health)

    Returns: String describing what happened
    Raises: AbilityOnCooldownError if ability was used recently
    """
    # Simple cooldown tracking: one use per battle
    if character.get("ability_on_cooldown", False):
        raise AbilityOnCooldownError("Special ability is on cooldown.")

    char_class = character.get("class", "").lower()

    if char_class == "warrior":
        result = warrior_power_strike(character, enemy)
    elif char_class == "mage":
        result = mage_fireball(character, enemy)
    elif char_class == "rogue":
        result = rogue_critical_strike(character, enemy)
    elif char_class == "cleric":
        result = cleric_heal(character)
    else:
        # If class not recognized, do nothing special
        result = "Nothing happened..."

    # Mark ability as used for this battle
    character["ability_on_cooldown"] = True
    return result


def warrior_power_strike(character, enemy):
    """Warrior special ability - double strength damage."""
    base = character.get("strength", 0)
    damage = max(1, base * 2)
    enemy["health"] = max(0, enemy.get("health", 0) - damage)
    return f"Warrior uses Power Strike for {damage} damage!"


def mage_fireball(character, enemy):
    """Mage special ability - double magic damage."""
    base = character.get("magic", 0)
    damage = max(1, base * 2)
    enemy["health"] = max(0, enemy.get("health", 0) - damage)
    return f"Mage casts Fireball for {damage} damage!"


def rogue_critical_strike(character, enemy):
    """Rogue special ability - 50% chance for triple strength damage."""
    base = character.get("strength", 0)
    if random.random() < 0.5:
        damage = max(1, base * 3)
        enemy["health"] = max(0, enemy.get("health", 0) - damage)
        return f"Rogue lands a Critical Strike for {damage} damage!"
    else:
        damage = max(1, base)
        enemy["health"] = max(0, enemy.get("health", 0) - damage)
        return f"Rogue strikes for {damage} damage (no crit)."


def cleric_heal(character):
    """Cleric special ability - restore 30 HP (not exceeding max_health)."""
    heal_amount = 30
    max_hp = character.get("max_health", 0)
    current_hp = character.get("health", 0)
    new_hp = min(max_hp, current_hp + heal_amount)
    actual_healed = new_hp - current_hp
    character["health"] = new_hp
    return f"Cleric heals for {actual_healed} HP!"


# ============================================================================
# COMBAT UTILITIES
# ============================================================================

def can_character_fight(character):
    """
    Check if character is in condition to fight

    Returns: True if health > 0 and not in battle
    """
    if character.get("health", 0) <= 0:
        return False
    if character.get("in_battle", False):
        return False
    return True


def get_victory_rewards(enemy):
    """
    Calculate rewards for defeating enemy

    Returns: Dictionary with 'xp' and 'gold'
    """
    xp = int(enemy.get("xp_reward", 0))
    gold = int(enemy.get("gold_reward", 0))
    return {"xp": xp, "gold": gold}


def display_combat_stats(character, enemy):
    """
    Display current combat status

    Shows both character and enemy health/stats
    """
    print(f"\n{character.get('name', 'Hero')}: "
          f"HP={character.get('health', 0)}/{character.get('max_health', 0)}")
    print(f"{enemy['name']}: HP={enemy.get('health', 0)}/{enemy.get('max_health', 0)}")


def display_battle_log(message):
    """
    Display a formatted battle message
    """
    print(f">>> {message}")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== COMBAT SYSTEM TEST ===")

    # Test enemy creation
    # try:
    #     goblin = create_enemy("goblin")
    #     print(f"Created {goblin['name']}")
    # except InvalidTargetError as e:
    #     print(f"Invalid enemy: {e}")

    # Test battle
    # test_char = {
    #     'name': 'Hero',
    #     'class': 'Warrior',
    #     'health': 120,
    #     'max_health': 120,
    #     'strength': 15,
    #     'magic': 5,
    #     'level': 1,
    #     'experience': 0,
    #     'gold': 0
    # }
    #
    # goblin = create_enemy("goblin")
    # battle = SimpleBattle(test_char, goblin)
    # try:
    #     result = battle.start_battle()
    #     print(f"Battle result: {result}")
    # except CharacterDeadError:
    #     print("Character is dead!")