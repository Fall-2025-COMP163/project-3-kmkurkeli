# AI Usage - AI assisted with explanations, debugging, code structure, and implementation guidance.
"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Starter Code

Name: [Kurkeli Kurkeli]

AI Usage: [AI assisted with explanations, debugging, code structure, and implementation guidance.]

This module handles inventory management, item usage, and equipment.
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)

# Maximum inventory size
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    """
    Add an item to character's inventory
    
    Args:
        character: Character dictionary
        item_id: Unique item identifier
    
    Returns: True if added successfully
    Raises: InventoryFullError if inventory is at max capacity
    """
    inventory = character.setdefault("inventory", [])

    if len(inventory) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")

    inventory.append(item_id)
    return True


def remove_item_from_inventory(character, item_id):
    """
    Remove an item from character's inventory
    
    Args:
        character: Character dictionary
        item_id: Item to remove
    
    Returns: True if removed successfully
    Raises: ItemNotFoundError if item not in inventory
    """
    inventory = character.setdefault("inventory", [])

    if item_id not in inventory:
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")

    inventory.remove(item_id)
    return True

def has_item(character, item_id):
    """
    Check if character has a specific item
    
    Returns: True if item in inventory, False otherwise
    """
    inventory = character.setdefault("inventory", [])
    return item_id in inventory

def count_item(character, item_id):
    """
    Count how many of a specific item the character has
    
    Returns: Integer count of item
    """
    inventory = character.setdefault("inventory", [])
    return inventory.count(item_id)

def get_inventory_space_remaining(character):
    """
    Calculate how many more items can fit in inventory
    
    Returns: Integer representing available slots
    """
    inventory = character.setdefault("inventory", [])
    return MAX_INVENTORY_SIZE - len(inventory)

def clear_inventory(character):
    """
    Remove all items from inventory
    
    Returns: List of removed items
    """
    inventory = character.setdefault("inventory", [])
    removed = list(inventory)
    inventory.clear()
    return removed

# ============================================================================
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    """
    Use a consumable item from inventory
    
    Args:
        character: Character dictionary
        item_id: Item to use
        item_data: Item information dictionary from game_data
    
    Item types and effects:
    - consumable: Apply effect and remove from inventory
    - weapon/armor: Cannot be "used", only equipped
    
    Returns: String describing what happened
    Raises: 
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'consumable'
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")

    item_type = item_data.get("type")
    if item_type != "consumable":
        raise InvalidItemTypeError("Only consumable items can be used.")

    effect_string = item_data.get("effect", "")
    stat_name, value = parse_item_effect(effect_string)

    apply_stat_effect(character, stat_name, value)
    remove_item_from_inventory(character, item_id)

    return f"Used {item_id}, {stat_name} changed by {value}."


def equip_weapon(character, item_id, item_data):
    """
    Equip a weapon
    
    Args:
        character: Character dictionary
        item_id: Weapon to equip
        item_data: Item information dictionary
    
    Weapon effect format: "strength:5" (adds 5 to strength)
    
    If character already has weapon equipped:
    - Unequip current weapon (remove bonus)
    - Add old weapon back to inventory
    
    Returns: String describing equipment change
    Raises:
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'weapon'
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")

    if item_data.get("type") != "weapon":
        raise InvalidItemTypeError("Item is not a weapon.")

    inventory = character.setdefault("inventory", [])

    # Unequip current weapon if any
    current_weapon = character.get("equipped_weapon")
    current_bonus = character.get("equipped_weapon_bonus")
    if current_weapon is not None:
        # Make sure inventory has space for the old weapon
        if len(inventory) >= MAX_INVENTORY_SIZE:
            raise InventoryFullError("No space to unequip current weapon.")
        inventory.append(current_weapon)

        # Remove previous bonus
        if current_bonus:
            stat_name, value = current_bonus
            apply_stat_effect(character, stat_name, -value)

    # Equip new weapon
    effect_string = item_data.get("effect", "")
    stat_name, value = parse_item_effect(effect_string)
    apply_stat_effect(character, stat_name, value)

    character["equipped_weapon"] = item_id
    character["equipped_weapon_bonus"] = (stat_name, value)

    remove_item_from_inventory(character, item_id)

    return f"Equipped weapon {item_id}."

def equip_armor(character, item_id, item_data):
    """
    Equip armor
    
    Args:
        character: Character dictionary
        item_id: Armor to equip
        item_data: Item information dictionary
    
    Armor effect format: "max_health:10" (adds 10 to max_health)
    
    If character already has armor equipped:
    - Unequip current armor (remove bonus)
    - Add old armor back to inventory
    
    Returns: String describing equipment change
    Raises:
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'armor'
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")

    if item_data.get("type") != "armor":
        raise InvalidItemTypeError("Item is not armor.")

    inventory = character.setdefault("inventory", [])

    # Unequip current armor if any
    current_armor = character.get("equipped_armor")
    current_bonus = character.get("equipped_armor_bonus")
    if current_armor is not None:
        if len(inventory) >= MAX_INVENTORY_SIZE:
            raise InventoryFullError("No space to unequip current armor.")
        inventory.append(current_armor)

        if current_bonus:
            stat_name, value = current_bonus
            apply_stat_effect(character, stat_name, -value)

    # Equip new armor
    effect_string = item_data.get("effect", "")
    stat_name, value = parse_item_effect(effect_string)
    apply_stat_effect(character, stat_name, value)

    character["equipped_armor"] = item_id
    character["equipped_armor_bonus"] = (stat_name, value)

    remove_item_from_inventory(character, item_id)

    return f"Equipped armor {item_id}."


def unequip_weapon(character):
    """
    Remove equipped weapon and return it to inventory
    
    Returns: Item ID that was unequipped, or None if no weapon equipped
    Raises: InventoryFullError if inventory is full
    """
    inventory = character.setdefault("inventory", [])
    current_weapon = character.get("equipped_weapon")

    if current_weapon is None:
        return None

    if len(inventory) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full; cannot unequip weapon.")

    # Remove stat bonuses
    bonus = character.get("equipped_weapon_bonus")
    if bonus:
        stat_name, value = bonus
        apply_stat_effect(character, stat_name, -value)

    inventory.append(current_weapon)
    character["equipped_weapon"] = None
    character["equipped_weapon_bonus"] = None

    return current_weapon


def unequip_armor(character):
    """
    Remove equipped armor and return it to inventory
    
    Returns: Item ID that was unequipped, or None if no armor equipped
    Raises: InventoryFullError if inventory is full
    """
    inventory = character.setdefault("inventory", [])
    current_armor = character.get("equipped_armor")

    if current_armor is None:
        return None

    if len(inventory) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full; cannot unequip armor.")

    bonus = character.get("equipped_armor_bonus")
    if bonus:
        stat_name, value = bonus
        apply_stat_effect(character, stat_name, -value)

    inventory.append(current_armor)
    character["equipped_armor"] = None
    character["equipped_armor_bonus"] = None

    return current_armor


# ============================================================================
# SHOP SYSTEM
# ============================================================================

def purchase_item(character, item_id, item_data):
    """
    Purchase an item from a shop
    
    Args:
        character: Character dictionary
        item_id: Item to purchase
        item_data: Item information with 'cost' field
    
    Returns: True if purchased successfully
    Raises:
        InsufficientResourcesError if not enough gold
        InventoryFullError if inventory is full
    """
    cost = int(item_data.get("cost", 0))
    gold = character.get("gold", 0)

    if gold < cost:
        raise InsufficientResourcesError("Not enough gold to purchase item.")

    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Inventory is full.")

    character["gold"] = gold - cost
    add_item_to_inventory(character, item_id)

    return True


def sell_item(character, item_id, item_data):
    """
    Sell an item for half its purchase cost
    
    Args:
        character: Character dictionary
        item_id: Item to sell
        item_data: Item information with 'cost' field
    
    Returns: Amount of gold received
    Raises: ItemNotFoundError if item not in inventory
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")

    cost = int(item_data.get("cost", 0))
    sell_price = cost // 2

    remove_item_from_inventory(character, item_id)
    character["gold"] = character.get("gold", 0) + sell_price

    return sell_price

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_item_effect(effect_string):
    """
    Parse item effect string into stat name and value
    
    Args:
        effect_string: String in format "stat_name:value"
    
    Returns: Tuple of (stat_name, value)
    Example: "health:20" → ("health", 20)
    """
    stat_name, value_str = effect_string.split(":", 1)
    value = int(value_str)
    return stat_name, value

def apply_stat_effect(character, stat_name, value):
    """
    Apply a stat modification to character
    
    Valid stats: health, max_health, strength, magic
    
    Note: health cannot exceed max_health
    """
    if stat_name not in character:
        # If stat doesn't exist, initialize then modify
        character[stat_name] = 0

    if stat_name == "health":
        character["health"] += value
        # health cannot exceed max_health
        max_hp = character.get("max_health", character["health"])
        if character["health"] > max_hp:
            character["health"] = max_hp
    elif stat_name == "max_health":
        character["max_health"] += value
        # If max_health drops below current health, clamp health
        if character.get("health", 0) > character["max_health"]:
            character["health"] = character["max_health"]
    else:
        # strength, magic, or other numeric stats
        character[stat_name] += value

def display_inventory(character, item_data_dict):
    """
    Display character's inventory in formatted way
    
    Args:
        character: Character dictionary
        item_data_dict: Dictionary of all item data
    
    Shows item names, types, and quantities
    """
    inventory = character.setdefault("inventory", [])

    if not inventory:
        output = "Inventory is empty."
        print(output)
        return output

    # Count quantities
    counts = {}
    for item_id in inventory:
        counts[item_id] = counts.get(item_id, 0) + 1

    lines = ["Inventory:"]
    for item_id, qty in sorted(counts.items()):
        item_info = item_data_dict.get(item_id, {})
        name = item_info.get("name", item_id)
        item_type = item_info.get("type", "unknown")
        lines.append(f"- {name} ({item_type}) x{qty}")

    output = "\n".join(lines)
    print(output)
    return output


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== INVENTORY SYSTEM TEST ===")
    
    # Test adding items
    # test_char = {'inventory': [], 'gold': 100, 'health': 80, 'max_health': 80}
    test_char = {
        "inventory": [],
        "gold": 100,
        "health": 50,
        "max_health": 80,
        "strength": 10,
        "magic": 5
    }

    test_items = {
        "health_potion": {
            "item_id": "health_potion",
            "name": "Health Potion",
            "type": "consumable",
            "effect": "health:20",
            "cost": 10
        }
    }

    try:
        purchase_item(test_char, "health_potion", test_items["health_potion"])
        print("Purchased health_potion")
        display_inventory(test_char, test_items)
        result = use_item(test_char, "health_potion", test_items["health_potion"])
        print(result)
        print(f"Health: {test_char['health']}/{test_char['max_health']}")
    except Exception as e:
        print("Test error:", e)

