# AI Usage - AI assisted with explanations, debugging, code structure, and implementation guidance.

"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Starter Code

Name: [Kurkeli Kurkeli]

AI Usage: [Helped with debugging, structuring my code and explanations.]

This module handles character creation, loading, and saving.
"""

import os
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# ============================================================================
# CHARACTER MANAGEMENT FUNCTIONS
# ============================================================================

def create_character(name, character_class):
    """
    Create a new character with stats based on class.
    """
    # Valid classes
    valid_classes = {
        "Warrior": {"health": 120, "strength": 15, "magic": 5},
        "Mage": {"health": 90, "strength": 8, "magic": 20},
        "Rogue": {"health": 100, "strength": 12, "magic": 10},
        "Cleric": {"health": 110, "strength": 10, "magic": 15}
    }

    # Validate class
    if character_class not in valid_classes:
        raise InvalidCharacterClassError(f"Invalid class: {character_class}")

    # Get the base stats
    base = valid_classes[character_class]

    # Build the character dictionary
    character = {
        "name": name,
        "class": character_class,
        "level": 1,
        "health": base["health"],
        "max_health": base["health"],
        "strength": base["strength"],
        "magic": base["magic"],
        "experience": 0,
        "gold": 100,
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }

    return character


def save_character(character, save_directory="data/save_games"):
    """
    Save character to file.

    Filename format: {character_name}_save.txt

    File format:
    NAME: character_name
    CLASS: class_name
    LEVEL: 1
    HEALTH: 120
    MAX_HEALTH: 120
    STRENGTH: 15
    MAGIC: 5
    EXPERIENCE: 0
    GOLD: 100
    INVENTORY: item1,item2,item3
    ACTIVE_QUESTS: quest1,quest2
    COMPLETED_QUESTS: quest1,quest2

    Returns: True if successful
    Raises: PermissionError, IOError (let them propagate)
    """
    # Make sure the save directory exists
    os.makedirs(save_directory, exist_ok=True)

    filename = f"{character['name']}_save.txt"
    filepath = os.path.join(save_directory, filename)

    # Helper to convert list -> comma separated string
    def list_to_str(value):
        if isinstance(value, list):
            return ",".join(str(v) for v in value)
        return str(value)

    # Let any file I/O exceptions propagate
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"NAME: {character['name']}\n")
        f.write(f"CLASS: {character['class']}\n")
        f.write(f"LEVEL: {character['level']}\n")
        f.write(f"HEALTH: {character['health']}\n")
        f.write(f"MAX_HEALTH: {character['max_health']}\n")
        f.write(f"STRENGTH: {character['strength']}\n")
        f.write(f"MAGIC: {character['magic']}\n")
        f.write(f"EXPERIENCE: {character['experience']}\n")
        f.write(f"GOLD: {character['gold']}\n")
        f.write(f"INVENTORY: {list_to_str(character['inventory'])}\n")
        f.write(f"ACTIVE_QUESTS: {list_to_str(character['active_quests'])}\n")
        f.write(f"COMPLETED_QUESTS: {list_to_str(character['completed_quests'])}\n")

    return True


def load_character(character_name, save_directory="data/save_games"):
    """
    Load character from save file.

    Args:
        character_name: Name of character to load
        save_directory: Directory containing save files

    Returns:
        Character dictionary

    Raises:
        CharacterNotFoundError if save file doesn't exist
        SaveFileCorruptedError if file exists but can't be read
        InvalidSaveDataError if data format is wrong
    """
    filename = f"{character_name}_save.txt"
    filepath = os.path.join(save_directory, filename)

    # 1) File not found
    if not os.path.exists(filepath):
        raise CharacterNotFoundError(f"Save file not found for: {character_name}")

    # 2) Try to read file
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        # File exists but can't be read
        raise SaveFileCorruptedError(f"Could not read save file for: {character_name}") from e

    # 3) Parse key: value lines into a dict of strings
    raw_data = {}
    try:
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if ":" not in line:
                raise InvalidSaveDataError("Invalid line format in save file")
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            raw_data[key] = value

        # 4) Build character dict with proper types
        character = {
            "name": raw_data["NAME"],
            "class": raw_data["CLASS"],
            "level": int(raw_data["LEVEL"]),
            "health": int(raw_data["HEALTH"]),
            "max_health": int(raw_data["MAX_HEALTH"]),
            "strength": int(raw_data["STRENGTH"]),
            "magic": int(raw_data["MAGIC"]),
            "experience": int(raw_data["EXPERIENCE"]),
            "gold": int(raw_data["GOLD"]),
            "inventory": [item for item in raw_data["INVENTORY"].split(",") if item],
            "active_quests": [q for q in raw_data["ACTIVE_QUESTS"].split(",") if q],
            "completed_quests": [q for q in raw_data["COMPLETED_QUESTS"].split(",") if q],
        }

    except (KeyError, ValueError) as e:
        # Missing keys or invalid number formats
        raise InvalidSaveDataError("Invalid or incomplete character data") from e

    return character

def list_saved_characters(save_directory="data/save_games"):
    """
    Get list of all saved character names.

    Returns:
        List of character names (without _save.txt extension)
    """
    if not os.path.isdir(save_directory):
        return []

    names = []
    for filename in os.listdir(save_directory):
        if filename.endswith("_save.txt"):
            name = filename[:-9]  # remove "_save.txt"
            names.append(name)

    return names

def delete_character(character_name, save_directory="data/save_games"):
    """
    Delete a character's save file.

    Returns:
        True if deleted successfully
    Raises:
        CharacterNotFoundError if character doesn't exist
    """
    filename = f"{character_name}_save.txt"
    filepath = os.path.join(save_directory, filename)

    if not os.path.exists(filepath):
        raise CharacterNotFoundError(f"Save file not found for: {character_name}")

    os.remove(filepath)
    return True

# ============================================================================
# CHARACTER OPERATIONS
# ============================================================================

def gain_experience(character, xp_amount):
    """
    Add experience to character and handle level ups.

    Raises:
        CharacterDeadError if character health is 0
    """
    # Dead characters can't gain XP
    if character["health"] <= 0:
        raise CharacterDeadError("Character is dead and cannot gain experience.")

    # Add XP
    character["experience"] += xp_amount

    # Handle possible multiple level-ups
    while character["experience"] >= character["level"] * 100:
        needed = character["level"] * 100
        character["experience"] -= needed
        character["level"] += 1

        # Stat increases on level up
        character["max_health"] += 10
        character["strength"] += 2
        character["magic"] += 2
        character["health"] = character["max_health"]

    return character

def add_gold(character, amount):
    """
    Add gold to character's inventory.

    Returns:
        New gold total
    Raises:
        ValueError if result would be negative
    """
    new_total = character["gold"] + amount
    if new_total < 0:
        raise ValueError("Gold cannot be negative.")

    character["gold"] = new_total
    return new_total

def heal_character(character, amount):
    """
    Heal character by specified amount.

    Returns:
        Actual amount healed
    """
    if amount <= 0:
        return 0

    missing = character["max_health"] - character["health"]
    if missing <= 0:
        return 0

    healed = min(amount, missing)
    character["health"] += healed
    return healed

def is_character_dead(character):
    """
    Check if character's health is 0 or below.

    Returns:
        True if dead, False if alive
    """
    return character["health"] <= 0

def revive_character(character):
    """
    Revive a dead character with 50% health.

    Returns:
        True if revived, False if character was already alive
    """
    if character["health"] > 0:
        return False

    # 50% of max health (integer)
    character["health"] = max(1, character["max_health"] // 2)
    return True

# ============================================================================
# VALIDATION
# ============================================================================

def validate_character_data(character):
    """
    Validate that character dictionary has all required fields.

    Returns:
        True if valid
    Raises:
        InvalidSaveDataError if missing fields or invalid types
    """
    required_keys = [
        "name", "class", "level", "health", "max_health",
        "strength", "magic", "experience", "gold",
        "inventory", "active_quests", "completed_quests"
    ]

    # Check keys
    for key in required_keys:
        if key not in character:
            raise InvalidSaveDataError(f"Missing field: {key}")

    # Check types
    int_fields = [
        "level", "health", "max_health",
        "strength", "magic", "experience", "gold"
    ]
    list_fields = ["inventory", "active_quests", "completed_quests"]

    try:
        for key in int_fields:
            if not isinstance(character[key], int):
                raise InvalidSaveDataError(f"Field {key} must be an int")

        for key in list_fields:
            if not isinstance(character[key], list):
                raise InvalidSaveDataError(f"Field {key} must be a list")

    except KeyError as e:
        raise InvalidSaveDataError("Character data is incomplete") from e

    return True

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== CHARACTER MANAGER TEST ===")
    
    # Test character creation
    # try:
    #     char = create_character("TestHero", "Warrior")
    #     print(f"Created: {char['name']} the {char['class']}")
    #     print(f"Stats: HP={char['health']}, STR={char['strength']}, MAG={char['magic']}")
    # except InvalidCharacterClassError as e:
    #     print(f"Invalid class: {e}")
    
    # Test saving
    # try:
    #     save_character(char)
    #     print("Character saved successfully")
    # except Exception as e:
    #     print(f"Save error: {e}")
    
    # Test loading
    # try:
    #     loaded = load_character("TestHero")
    #     print(f"Loaded: {loaded['name']}")
    # except CharacterNotFoundError:
    #     print("Character not found")
    # except SaveFileCorruptedError:
    #     print("Save file corrupted")

