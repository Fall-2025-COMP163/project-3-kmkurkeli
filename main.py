# AI Usage - AI assisted with explanations, debugging, code structure, and implementation guidance.
"""
COMP 163 - Project 3: Quest Chronicles
Main Game Module - Starter Code

Name: [Kurkeli Kurkeli]

AI Usage: [AI assisted with explanations, debugging, code structure, and implementation guidance.]

This is the main game file that ties all modules together.
Demonstrates module integration and complete game flow.
"""

# Import all our custom modules
import character_manager
import inventory_system
import quest_handler
import combat_system
import game_data
from custom_exceptions import *

# ============================================================================
# GAME STATE
# ============================================================================

# Global variables for game data
current_character = None
all_quests = {}
all_items = {}
game_running = False

# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    """
    Display main menu and get player choice
    
    Options:
    1. New Game
    2. Load Game
    3. Exit
    
    Returns: Integer choice (1-3)
    """
    while True:
        print("\n=== MAIN MENU ===")
        print("1. New Game")
        print("2. Load Game")
        print("3. Exit")
        choice = input("Enter choice (1-3): ").strip()

        if choice in {"1", "2", "3"}:
            return int(choice)
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def new_game():
    """
    Start a new game
    
    Prompts for:
    - Character name
    - Character class
    
    Creates character and starts game loop
    """
    global current_character

    print("\n=== NEW GAME ===")
    name = input("Enter your character's name: ").strip()
    if not name:
        name = "Hero"

    print("\nChoose your class:")
    print("1. Warrior")
    print("2. Mage")
    print("3. Rogue")
    print("4. Cleric")
    class_choice = input("Enter choice (1-4): ").strip()

    class_map = {
        "1": "Warrior",
        "2": "Mage",
        "3": "Rogue",
        "4": "Cleric"
    }
    char_class = class_map.get(class_choice, "Warrior")

    try:
        character = character_manager.create_character(name, char_class)
        current_character = character
        print(f"\nCreated {char_class} named {name}!")
        save_game()
        game_loop()
    except InvalidCharacterClassError as e:
        print(f"Error creating character: {e}")

def load_game():
    """
    Load an existing saved game
    
    Shows list of saved characters
    Prompts user to select one
    """
    global current_character

    print("\n=== LOAD GAME ===")
    try:
        saved_names = character_manager.list_saved_characters()
    except Exception as e:
        print(f"Error listing saved games: {e}")
        return

    if not saved_names:
        print("No saved characters found.")
        return

    print("\nSaved Characters:")
    for idx, name in enumerate(saved_names, start=1):
        print(f"{idx}. {name}")

    while True:
        choice = input("Select a character number (or 'b' to go back): ").strip()
        if choice.lower() == "b":
            return
        try:
            idx = int(choice)
            if 1 <= idx <= len(saved_names):
                selected_name = saved_names[idx - 1]
                break
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a valid number or 'b' to go back.")

    try:
        current_character = character_manager.load_character(selected_name)
        print(f"\nLoaded character: {selected_name}")
        game_loop()
    except CharacterNotFoundError as e:
        print(f"Error: {e}")
    except SaveFileCorruptedError as e:
        print(f"Save file corrupted: {e}")


# ============================================================================
# GAME LOOP
# ============================================================================

def game_loop():
    """
    Main game loop - shows game menu and processes actions
    """
    global game_running, current_character

    if current_character is None:
        print("No character loaded.")
        return


    game_running = True
    print(f"\nWelcome back, {current_character.get('name', 'Hero')}!")

    while game_running:
        choice = game_menu()

        if choice == 1:
            view_character_stats()
        elif choice == 2:
            view_inventory()
        elif choice == 3:
            quest_menu()
        elif choice == 4:
            explore()
        elif choice == 5:
            shop()
        elif choice == 6:
            print("Saving game and returning to main menu...")
            save_game()
            game_running = False
        else:
            print("Invalid choice.")

        # Auto-save after each action
        if game_running:
            save_game()

def game_menu():
    """
    Display game menu and get player choice
    
    Options:
    1. View Character Stats
    2. View Inventory
    3. Quest Menu
    4. Explore (Find Battles)
    5. Shop
    6. Save and Quit
    
    Returns: Integer choice (1-6)
    """
    while True:
        print("\n=== GAME MENU ===")
        print("1. View Character Stats")
        print("2. View Inventory")
        print("3. Quest Menu")
        print("4. Explore (Find Battles)")
        print("5. Shop")
        print("6. Save and Quit")
        choice = input("Enter choice (1-6): ").strip()

        if choice in {"1", "2", "3", "4", "5", "6"}:
            return int(choice)
        else:
            print("Invalid choice. Please enter 1-6.")


# ============================================================================
# GAME ACTIONS
# ============================================================================

def view_character_stats():
    """Display character information"""
    global current_character

    char = current_character
    print("\n=== CHARACTER STATS ===")
    print(f"Name:  {char.get('name', 'Unknown')}")
    print(f"Class: {char.get('class', 'Unknown')}")
    print(f"Level: {char.get('level', 1)}")
    print(f"XP:    {char.get('experience', 0)}")
    print(f"HP:    {char.get('health', 0)}/{char.get('max_health', 0)}")
    print(f"STR:   {char.get('strength', 0)}")
    print(f"MAG:   {char.get('magic', 0)}")
    print(f"Gold:  {char.get('gold', 0)}")

    # Quest progress
    try:
        completion_pct = quest_handler.get_quest_completion_percentage(char, all_quests)
        totals = quest_handler.get_total_quest_rewards_earned(char, all_quests)
        print(f"\nQuest Completion: {completion_pct:.1f}%")
        print(f"Quest Rewards Earned: {totals['total_xp']} XP, {totals['total_gold']} gold")
    except Exception:
        # If quests not fully initialized, just skip
        pass


def view_inventory():
    """Display and manage inventory"""
    global current_character, all_items

    print("\n=== INVENTORY ===")
    inventory_system.display_inventory(current_character, all_items)

    while True:
        print("\nInventory Options:")
        print("1. Use Item")
        print("2. Equip Weapon")
        print("3. Equip Armor")
        print("4. Drop Item")
        print("5. Back")
        choice = input("Enter choice (1-5): ").strip()

        if choice == "5":
            break

        item_id = input("Enter item ID: ").strip()
        if not item_id:
            print("No item ID entered.")
            continue

        if choice == "1":
            # Use item
            item_info = all_items.get(item_id)
            if not item_info:
                print("Unknown item.")
                continue
            try:
                result = inventory_system.use_item(current_character, item_id, item_info)
                print(result)
            except ItemNotFoundError as e:
                print(f"Error: {e}")
            except InvalidItemTypeError as e:
                print(f"Error: {e}")
        elif choice == "2":
            # Equip weapon
            item_info = all_items.get(item_id)
            if not item_info:
                print("Unknown item.")
                continue
            try:
                result = inventory_system.equip_weapon(current_character, item_id, item_info)
                print(result)
            except (ItemNotFoundError, InvalidItemTypeError, InventoryFullError) as e:
                print(f"Error: {e}")
        elif choice == "3":
            # Equip armor
            item_info = all_items.get(item_id)
            if not item_info:
                print("Unknown item.")
                continue
            try:
                result = inventory_system.equip_armor(current_character, item_id, item_info)
                print(result)
            except (ItemNotFoundError, InvalidItemTypeError, InventoryFullError) as e:
                print(f"Error: {e}")
        elif choice == "4":
            # Drop item (remove from inventory)
            try:
                inventory_system.remove_item_from_inventory(current_character, item_id)
                print(f"Dropped {item_id}.")
            except ItemNotFoundError as e:
                print(f"Error: {e}")
        else:
            print("Invalid choice.")

        # Re-display inventory after action
        inventory_system.display_inventory(current_character, all_items)

def quest_menu():
    """Quest management menu"""
    global current_character, all_quests

    while True:
        print("\n=== QUEST MENU ===")
        print("1. View Active Quests")
        print("2. View Available Quests")
        print("3. View Completed Quests")
        print("4. Accept Quest")
        print("5. Abandon Quest")
        print("6. Complete Quest (for testing)")
        print("7. Back")
        choice = input("Enter choice (1-7): ").strip()

        if choice == "1":
            active = quest_handler.get_active_quests(current_character, all_quests)
            quest_handler.display_quest_list(active)
        elif choice == "2":
            available = quest_handler.get_available_quests(current_character, all_quests)
            quest_handler.display_quest_list(available)
        elif choice == "3":
            completed = quest_handler.get_completed_quests(current_character, all_quests)
            quest_handler.display_quest_list(completed)
        elif choice == "4":
            quest_id = input("Enter quest ID to accept: ").strip()
            try:
                quest_handler.accept_quest(current_character, quest_id, all_quests)
                print(f"Accepted quest: {quest_id}")
            except (QuestNotFoundError, InsufficientLevelError,
                    QuestRequirementsNotMetError, QuestAlreadyCompletedError) as e:
                print(f"Error: {e}")
        elif choice == "5":
            quest_id = input("Enter quest ID to abandon: ").strip()
            try:
                quest_handler.abandon_quest(current_character, quest_id)
                print(f"Abandoned quest: {quest_id}")
            except QuestNotActiveError as e:
                print(f"Error: {e}")
        elif choice == "6":
            # For testing: manually mark quest as completed and grant rewards
            quest_id = input("Enter quest ID to complete: ").strip()
            try:
                rewards = quest_handler.complete_quest(current_character, quest_id, all_quests)
                print(f"Completed quest: {quest_id}")
                print(f"Rewards: {rewards['reward_xp']} XP, {rewards['reward_gold']} gold")
            except (QuestNotFoundError, QuestNotActiveError) as e:
                print(f"Error: {e}")
        elif choice == "7":
            break
        else:
            print("Invalid choice.")

def explore():
    """Find and fight random enemies"""
    global current_character

    print("\n=== EXPLORE ===")

    if not combat_system.can_character_fight(current_character):
        print("You are not in condition to fight (dead or already in battle).")
        return

    level = current_character.get("level", 1)
    enemy = combat_system.get_random_enemy_for_level(level)
    print(f"A wild {enemy['name']} appears!")

    battle = combat_system.SimpleBattle(current_character, enemy)
    try:
        result = battle.start_battle()
        print(f"Battle result: {result['winner']}")
    except CharacterDeadError:
        print("You cannot fight because you are dead.")
    finally:
        if current_character.get("health", 0) <= 0:
            handle_character_death()

def shop():
    """Shop menu for buying/selling items"""
    global current_character, all_items

    print("\n=== SHOP ===")
    while True:
        print(f"\nYou have {current_character.get('gold', 0)} gold.")
        print("1. Buy Item")
        print("2. Sell Item")
        print("3. Back")
        choice = input("Enter choice (1-3): ").strip()

        if choice == "1":
            print("\nItems for sale:")
            for item_id, data in all_items.items():
                print(f"- {item_id}: {data.get('name', item_id)} "
                      f"({data.get('type', 'unknown')}) - {data.get('cost', 0)} gold")
            item_id = input("Enter item ID to buy: ").strip()
            item_info = all_items.get(item_id)
            if not item_info:
                print("Unknown item.")
                continue
            try:
                inventory_system.purchase_item(current_character, item_id, item_info)
                print(f"Purchased {item_id}.")
            except (InsufficientResourcesError, InventoryFullError) as e:
                print(f"Error: {e}")
        elif choice == "2":
            # Selling items from inventory
            inventory_system.display_inventory(current_character, all_items)
            item_id = input("Enter item ID to sell: ").strip()
            item_info = all_items.get(item_id)
            if not item_info:
                print("Unknown item.")
                continue
            try:
                gold_received = inventory_system.sell_item(current_character, item_id, item_info)
                print(f"Sold {item_id} for {gold_received} gold.")
            except ItemNotFoundError as e:
                print(f"Error: {e}")
        elif choice == "3":
            break
        else:
            print("Invalid choice.")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def save_game():
    """Save current game state"""
    global current_character

    if current_character is None:
        return

    try:
        character_manager.save_character(current_character)
        # Optional: print a quiet confirmation
        # print("Game saved.")
    except Exception as e:
        print(f"Error saving game: {e}")

def load_game_data():
    """Load all quest and item data from files"""
    global all_quests, all_items

    try:
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()
    except MissingDataFileError:
        # Create default files, then reload
        game_data.create_default_data_files()
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()
    except InvalidDataFormatError:
        # Let main() handle this
        raise

def handle_character_death():
    """Handle character death"""
    global current_character, game_running

    print("\n=== YOU HAVE FALLEN IN BATTLE ===")
    print("1. Revive (costs 20 gold)")
    print("2. Quit to main menu")
    choice = input("Enter choice (1-2): ").strip()

    if choice == "1":
        cost = 20
        if current_character.get("gold", 0) < cost:
            print("You do not have enough gold to revive.")
            game_running = False
            return
        current_character["gold"] -= cost
        character_manager.revive_character(current_character)
        print("You have been revived!")
    else:
        print("Returning to main menu...")
        game_running = False


def display_welcome():
    """Display welcome message"""
    print("=" * 50)
    print("     QUEST CHRONICLES - A MODULAR RPG ADVENTURE")
    print("=" * 50)
    print("\nWelcome to Quest Chronicles!")
    print("Build your character, complete quests, and become a legend!")
    print()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main game execution function"""
    
    # Display welcome message
    display_welcome()
    
    # Load game data
    try:
        load_game_data()
        print("Game data loaded successfully!")
    except MissingDataFileError:
        print("Creating default game data...")
        game_data.create_default_data_files()
        load_game_data()
    except InvalidDataFormatError as e:
        print(f"Error loading game data: {e}")
        print("Please check data files for errors.")
        return
    
    # Main menu loop
    while True:
        choice = main_menu()
        
        if choice == 1:
            new_game()
        elif choice == 2:
            load_game()
        elif choice == 3:
            print("\nThanks for playing Quest Chronicles!")
            break
        else:
            print("Invalid choice. Please select 1-3.")

if __name__ == "__main__":
    main()

