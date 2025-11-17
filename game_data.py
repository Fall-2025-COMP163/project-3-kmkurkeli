# AI Usage - AI assisted with explanations, debugging, code structure, and implementation guidance.
"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Starter Code

Name: [Kurkeli Kurkeli]

AI Usage: [AI assisted with explanations, debugging, code structure, and implementation guidance.]

This module handles loading and validating game data from text files.
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_quests(filename="data/quests.txt"):
    """
    Load quest data from file.

    Returns:
        Dictionary of quests {quest_id: quest_data_dict}

    Raises:
        MissingDataFileError, InvalidDataFormatError, CorruptedDataError
    """
    # 1) File doesn’t exist at all
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Quest file not found: {filename}")

    # 2) Try to read file safely
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        # File exists but cannot be read
        raise CorruptedDataError(f"Could not read quest file: {filename}") from e

    # 3) Split into blocks separated by blank lines
    blocks = []
    current = []
    for line in lines:
        if line.strip() == "":
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(line)
    if current:
        blocks.append(current)

    if not blocks:
        raise InvalidDataFormatError("Quest file is empty or has no valid entries")

    # 4) Parse each block using helper
    quests = {}
    for block in blocks:
        quest = parse_quest_block(block)
        quest_id = quest["quest_id"]
        quests[quest_id] = quest

    return quests

def load_items(filename="data/items.txt"):
    """
    Load item data from file.

    Returns:
        Dictionary of items {item_id: item_data_dict}

    Raises:
        MissingDataFileError, InvalidDataFormatError, CorruptedDataError
    """
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Item file not found: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        raise CorruptedDataError(f"Could not read item file: {filename}") from e

    blocks = []
    current = []
    for line in lines:
        if line.strip() == "":
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(line)
    if current:
        blocks.append(current)

    if not blocks:
        raise InvalidDataFormatError("Item file is empty or has no valid entries")

    items = {}
    for block in blocks:
        item = parse_item_block(block)
        item_id = item["item_id"]
        items[item_id] = item

    return items

def validate_quest_data(quest_dict):
    """
    Validate that quest dictionary has all required fields.

    Returns:
        True if valid
    Raises:
        InvalidDataFormatError if missing required fields or invalid types
    """
    required_keys = [
        "quest_id",
        "title",
        "description",
        "reward_xp",
        "reward_gold",
        "required_level",
        "prerequisite",
    ]

    for key in required_keys:
        if key not in quest_dict:
            raise InvalidDataFormatError(f"Missing quest field: {key}")

    int_fields = ["reward_xp", "reward_gold", "required_level"]

    try:
        for key in int_fields:
            if not isinstance(quest_dict[key], int):
                raise InvalidDataFormatError(f"Quest field {key} must be an int")
    except KeyError as e:
        raise InvalidDataFormatError("Quest data incomplete") from e

    # prerequisite can be None or a string
    prereq = quest_dict["prerequisite"]
    if prereq is not None and not isinstance(prereq, str):
        raise InvalidDataFormatError("prerequisite must be None or str")

    return True

def validate_item_data(item_dict):
    """
    Validate that item dictionary has all required fields.

    Returns:
        True if valid
    Raises:
        InvalidDataFormatError if missing required fields or invalid type
    """
    required_keys = [
        "item_id",
        "name",
        "type",
        "effect",
        "cost",
        "description",
    ]

    for key in required_keys:
        if key not in item_dict:
            raise InvalidDataFormatError(f"Missing item field: {key}")

    # cost must be int
    if not isinstance(item_dict["cost"], int):
        raise InvalidDataFormatError("Item cost must be an int")

    # type must be valid
    if item_dict["type"] not in ("weapon", "armor", "consumable"):
        raise InvalidDataFormatError("Invalid item type")

    return True

def create_default_data_files():
    """
    Create default data files if they don't exist.

    Creates:
        data/quests.txt
        data/items.txt

    Raises:
        Any OSError will propagate (e.g., permission issues)
    """
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)

    quests_path = os.path.join(data_dir, "quests.txt")
    items_path = os.path.join(data_dir, "items.txt")

    # Only create if missing so we don't overwrite student-customized data
    if not os.path.exists(quests_path):
        with open(quests_path, "w", encoding="utf-8") as f:
            f.write(
                "QUEST_ID: quest_intro\n"
                "TITLE: First Steps\n"
                "DESCRIPTION: Meet the village elder.\n"
                "REWARD_XP: 50\n"
                "REWARD_GOLD: 20\n"
                "REQUIRED_LEVEL: 1\n"
                "PREREQUISITE: NONE\n\n"
                "QUEST_ID: quest_hunt_goblins\n"
                "TITLE: Goblin Trouble\n"
                "DESCRIPTION: Clear the goblins from the forest.\n"
                "REWARD_XP: 150\n"
                "REWARD_GOLD: 75\n"
                "REQUIRED_LEVEL: 2\n"
                "PREREQUISITE: quest_intro\n"
            )

    if not os.path.exists(items_path):
        with open(items_path, "w", encoding="utf-8") as f:
            f.write(
                "ITEM_ID: sword_basic\n"
                "NAME: Iron Sword\n"
                "TYPE: weapon\n"
                "EFFECT: strength:5\n"
                "COST: 100\n"
                "DESCRIPTION: A simple but reliable sword.\n\n"
                "ITEM_ID: robe_apprentice\n"
                "NAME: Apprentice Robe\n"
                "TYPE: armor\n"
                "EFFECT: health:10\n"
                "COST: 80\n"
                "DESCRIPTION: Light robes for beginning mages.\n\n"
                "ITEM_ID: potion_small\n"
                "NAME: Small Health Potion\n"
                "TYPE: consumable\n"
                "EFFECT: health:20\n"
                "COST: 30\n"
                "DESCRIPTION: Restores a small amount of health.\n"
            )

    return True

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_quest_block(lines):
    """
    Parse a block of lines into a quest dictionary.

    Args:
        lines: List of strings representing one quest

    Returns:
        Dictionary with quest data

    Raises:
        InvalidDataFormatError if parsing fails
    """
    raw = {}

    try:
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if ":" not in line:
                raise InvalidDataFormatError("Invalid quest line format")
            key, value = line.split(":", 1)
            key = key.strip().upper()
            value = value.strip()
            raw[key] = value

        # Required keys in the raw block (as they appear in the file)
        required_raw_keys = [
            "QUEST_ID",
            "TITLE",
            "DESCRIPTION",
            "REWARD_XP",
            "REWARD_GOLD",
            "REQUIRED_LEVEL",
            "PREREQUISITE",
        ]
        for k in required_raw_keys:
            if k not in raw:
                raise InvalidDataFormatError(f"Missing quest field: {k}")

        # Build final quest dict with proper types
        quest = {
            "quest_id": raw["QUEST_ID"],
            "title": raw["TITLE"],
            "description": raw["DESCRIPTION"],
            "reward_xp": int(raw["REWARD_XP"]),
            "reward_gold": int(raw["REWARD_GOLD"]),
            "required_level": int(raw["REQUIRED_LEVEL"]),
            "prerequisite": None
            if raw["PREREQUISITE"].upper() == "NONE"
            else raw["PREREQUISITE"],
        }

    except (ValueError, KeyError) as e:
        # Bad numbers or missing keys
        raise InvalidDataFormatError("Invalid quest data format") from e

    return quest

def parse_item_block(lines):
    """
    Parse a block of lines into an item dictionary.

    Args:
        lines: List of strings representing one item

    Returns:
        Dictionary with item data

    Raises:
        InvalidDataFormatError if parsing fails
    """
    raw = {}

    try:
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if ":" not in line:
                raise InvalidDataFormatError("Invalid item line format")
            key, value = line.split(":", 1)
            key = key.strip().upper()
            value = value.strip()
            raw[key] = value

        required_raw_keys = [
            "ITEM_ID",
            "NAME",
            "TYPE",
            "EFFECT",
            "COST",
            "DESCRIPTION",
        ]
        for k in required_raw_keys:
            if k not in raw:
                raise InvalidDataFormatError(f"Missing item field: {k}")

        # basic type checking
        item_type = raw["TYPE"].lower()
        if item_type not in ("weapon", "armor", "consumable"):
            raise InvalidDataFormatError("Invalid item type")

        item = {
            "item_id": raw["ITEM_ID"],
            "name": raw["NAME"],
            "type": item_type,
            "effect": raw["EFFECT"],       # keep as string like "strength:5"
            "cost": int(raw["COST"]),
            "description": raw["DESCRIPTION"],
        }

    except (ValueError, KeyError) as e:
        raise InvalidDataFormatError("Invalid item data format") from e

    return item

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== GAME DATA MODULE TEST ===")
    
    # Test creating default files
    # create_default_data_files()
    
    # Test loading quests
    # try:
    #     quests = load_quests()
    #     print(f"Loaded {len(quests)} quests")
    # except MissingDataFileError:
    #     print("Quest file not found")
    # except InvalidDataFormatError as e:
    #     print(f"Invalid quest format: {e}")
    
    # Test loading items
    # try:
    #     items = load_items()
    #     print(f"Loaded {len(items)} items")
    # except MissingDataFileError:
    #     print("Item file not found")
    # except InvalidDataFormatError as e:
    #     print(f"Invalid item format: {e}")

