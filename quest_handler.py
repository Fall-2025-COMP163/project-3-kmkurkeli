# AI Usage - AI assisted with explanations, debugging, code structure, and implementation guidance.
"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module - Starter Code

Name: [Kurkeli Kurkeli]

AI Usage: [AI assisted with explanations, debugging, code structure, and implementation guidance.]

This module handles quest management, dependencies, and completion.
"""

from custom_exceptions import (
    QuestNotFoundError,
    QuestRequirementsNotMetError,
    QuestAlreadyCompletedError,
    QuestNotActiveError,
    InsufficientLevelError
)

from character_manager import gain_experience, add_gold


# ============================================================================
# QUEST MANAGEMENT
# ============================================================================

def accept_quest(character, quest_id, quest_data_dict):
    """
    Accept a new quest
    
    Args:
        character: Character dictionary
        quest_id: Quest to accept
        quest_data_dict: Dictionary of all quest data
    
    Requirements to accept quest:
    - Character level >= quest required_level
    - Prerequisite quest completed (if any)
    - Quest not already completed
    - Quest not already active
    
    Returns: True if quest accepted
    Raises:
        QuestNotFoundError if quest_id not in quest_data_dict
        InsufficientLevelError if character level too low
        QuestRequirementsNotMetError if prerequisite not completed
        QuestAlreadyCompletedError if quest already done
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")

    quest = quest_data_dict[quest_id]
    character.setdefault("active_quests", [])
    character.setdefault("completed_quests", [])

    # Level requirement
    required_level = quest.get("required_level", 1)
    if character.get("level", 1) < required_level:
        raise InsufficientLevelError(
            f"Level {required_level} required for quest '{quest_id}'."
        )

    # Already completed?
    if quest_id in character["completed_quests"]:
        raise QuestAlreadyCompletedError(f"Quest '{quest_id}' already completed.")

    # Already active?
    if quest_id in character["active_quests"]:
        # Treat as requirements not met (cannot accept twice)
        raise QuestRequirementsNotMetError(f"Quest '{quest_id}' is already active.")

    # Prerequisite
    prereq = quest.get("prerequisite", "NONE")
    if prereq and prereq != "NONE":
        if prereq not in character["completed_quests"]:
            raise QuestRequirementsNotMetError(
                f"Prerequisite quest '{prereq}' not completed."
            )

    character["active_quests"].append(quest_id)
    return True


def complete_quest(character, quest_id, quest_data_dict):
    """
    Complete an active quest and grant rewards
    
    Args:
        character: Character dictionary
        quest_id: Quest to complete
        quest_data_dict: Dictionary of all quest data
    
    Rewards:
    - Experience points (reward_xp)
    - Gold (reward_gold)
    
    Returns: Dictionary with reward information
    Raises:
        QuestNotFoundError if quest_id not in quest_data_dict
        QuestNotActiveError if quest not in active_quests
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")

    character.setdefault("active_quests", [])
    character.setdefault("completed_quests", [])

    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError(f"Quest '{quest_id}' is not active.")

    quest = quest_data_dict[quest_id]

    # Remove from active, add to completed
    character["active_quests"].remove(quest_id)
    if quest_id not in character["completed_quests"]:
        character["completed_quests"].append(quest_id)

    # Rewards
    reward_xp = int(quest.get("reward_xp", 0))
    reward_gold = int(quest.get("reward_gold", 0))

    # Use character_manager helpers
    gain_experience(character, reward_xp)
    add_gold(character, reward_gold)

    return {
        "quest_id": quest_id,
        "reward_xp": reward_xp,
        "reward_gold": reward_gold
    }


def abandon_quest(character, quest_id):
    """
    Remove a quest from active quests without completing it
    
    Returns: True if abandoned
    Raises: QuestNotActiveError if quest not active
    """
    character.setdefault("active_quests", [])

    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError(f"Quest '{quest_id}' is not active.")

    character["active_quests"].remove(quest_id)
    return True

def get_active_quests(character, quest_data_dict):
    """
    Get full data for all active quests
    
    Returns: List of quest dictionaries for active quests
    """
    character.setdefault("active_quests", [])
    result = []

    for qid in character["active_quests"]:
        if qid in quest_data_dict:
            result.append(quest_data_dict[qid])

    return result

def get_completed_quests(character, quest_data_dict):
    """
    Get full data for all completed quests
    
    Returns: List of quest dictionaries for completed quests
    """
    character.setdefault("completed_quests", [])
    result = []

    for qid in character["completed_quests"]:
        if qid in quest_data_dict:
            result.append(quest_data_dict[qid])

    return result

def get_available_quests(character, quest_data_dict):
    """
    Get quests that character can currently accept
    
    Available = meets level req + prerequisite done + not completed + not active
    
    Returns: List of quest dictionaries
    """
    available = []

    for qid in quest_data_dict:
        if can_accept_quest(character, qid, quest_data_dict):
            available.append(quest_data_dict[qid])

    return available

# ============================================================================
# QUEST TRACKING
# ============================================================================

def is_quest_completed(character, quest_id):
    """
    Check if a specific quest has been completed
    
    Returns: True if completed, False otherwise
    """
    character.setdefault("completed_quests", [])
    return quest_id in character["completed_quests"]


def is_quest_active(character, quest_id):
    """
    Check if a specific quest is currently active
    
    Returns: True if active, False otherwise
    """
    character.setdefault("active_quests", [])
    return quest_id in character["active_quests"]

def can_accept_quest(character, quest_id, quest_data_dict):
    """
    Check if character meets all requirements to accept quest
    
    Returns: True if can accept, False otherwise
    Does NOT raise exceptions - just returns boolean
    """
    if quest_id not in quest_data_dict:
        return False

    quest = quest_data_dict[quest_id]
    character.setdefault("active_quests", [])
    character.setdefault("completed_quests", [])

    # Level requirement
    required_level = quest.get("required_level", 1)
    if character.get("level", 1) < required_level:
        return False

    # Already completed or active
    if quest_id in character["completed_quests"]:
        return False
    if quest_id in character["active_quests"]:
        return False

    # Prerequisite requirement
    prereq = quest.get("prerequisite", "NONE")
    if prereq and prereq != "NONE":
        if prereq not in character["completed_quests"]:
            return False

    return True


def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    """
    Get the full chain of prerequisites for a quest
    
    Returns: List of quest IDs in order [earliest_prereq, ..., quest_id]
    Example: If Quest C requires Quest B, which requires Quest A:
             Returns ["quest_a", "quest_b", "quest_c"]
    
    Raises: QuestNotFoundError if quest doesn't exist
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")

    chain = []
    current_id = quest_id

    while True:
        if current_id not in quest_data_dict:
            raise QuestNotFoundError(f"Quest '{current_id}' not found.")
        chain.append(current_id)
        quest = quest_data_dict[current_id]
        prereq = quest.get("prerequisite", "NONE")
        if not prereq or prereq == "NONE":
            break
        current_id = prereq

    # We built from final → earliest; reverse to get earliest first
    chain.reverse()
    return chain


# ============================================================================
# QUEST STATISTICS
# ============================================================================

def get_quest_completion_percentage(character, quest_data_dict):
    """
    Calculate what percentage of all quests have been completed
    
    Returns: Float between 0 and 100
    """
    total_quests = len(quest_data_dict)
    if total_quests == 0:
        return 0.0

    character.setdefault("completed_quests", [])
    completed = sum(1 for qid in character["completed_quests"]
                    if qid in quest_data_dict)

    return (completed / total_quests) * 100.0

def get_total_quest_rewards_earned(character, quest_data_dict):
    """
    Calculate total XP and gold earned from completed quests
    
    Returns: Dictionary with 'total_xp' and 'total_gold'
    """
    character.setdefault("completed_quests", [])
    total_xp = 0
    total_gold = 0

    for qid in character["completed_quests"]:
        quest = quest_data_dict.get(qid)
        if quest is not None:
            total_xp += int(quest.get("reward_xp", 0))
            total_gold += int(quest.get("reward_gold", 0))

    return {"total_xp": total_xp, "total_gold": total_gold}


def get_quests_by_level(quest_data_dict, min_level, max_level):
    """
    Get all quests within a level range
    
    Returns: List of quest dictionaries
    """
    quests = []
    for quest in quest_data_dict.values():
        level = quest.get("required_level", 1)
        if min_level <= level <= max_level:
            quests.append(quest)
    return quests

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_quest_info(quest_data):
    """
    Display formatted quest information
    
    Shows: Title, Description, Rewards, Requirements
    """
    print(f"\n=== {quest_data['title']} ===")
    print(f"Description: {quest_data['description']}")
    print(f"Required Level: {quest_data.get('required_level', 1)}")
    prereq = quest_data.get("prerequisite", "NONE")
    print(f"Prerequisite: {prereq}")
    print(f"Rewards: {quest_data.get('reward_xp', 0)} XP, "
          f"{quest_data.get('reward_gold', 0)} gold")

def display_quest_list(quest_list):
    """
    Display a list of quests in summary format
    
    Shows: Title, Required Level, Rewards
    """
    if not quest_list:
        print("No quests to display.")
        return

    print("\nQuests:")
    for quest in quest_list:
        title = quest["title"]
        level = quest.get("required_level", 1)
        xp = quest.get("reward_xp", 0)
        gold = quest.get("reward_gold", 0)
        print(f"- {title} (Level {level}) -> {xp} XP, {gold} gold")


def display_character_quest_progress(character, quest_data_dict):
    """
    Display character's quest statistics and progress
    
    Shows:
    - Active quests count
    - Completed quests count
    - Completion percentage
    - Total rewards earned
    """
    character.setdefault("active_quests", [])
    character.setdefault("completed_quests", [])

    active_count = len(character["active_quests"])
    completed_count = len(character["completed_quests"])
    completion_pct = get_quest_completion_percentage(character, quest_data_dict)
    totals = get_total_quest_rewards_earned(character, quest_data_dict)

    print("\n=== Quest Progress ===")
    print(f"Active quests: {active_count}")
    print(f"Completed quests: {completed_count}")
    print(f"Completion: {completion_pct:.1f}%")
    print(f"Total rewards earned: {totals['total_xp']} XP, "
          f"{totals['total_gold']} gold")

# ============================================================================
# VALIDATION
# ============================================================================

def validate_quest_prerequisites(quest_data_dict):
    """
    Validate that all quest prerequisites exist
    
    Checks that every prerequisite (that's not "NONE") refers to a real quest
    
    Returns: True if all valid
    Raises: QuestNotFoundError if invalid prerequisite found
    """
    for quest_id, quest in quest_data_dict.items():
        prereq = quest.get("prerequisite", "NONE")
        if prereq and prereq != "NONE":
            if prereq not in quest_data_dict:
                raise QuestNotFoundError(
                    f"Quest '{quest_id}' has invalid prerequisite '{prereq}'."
                )
    return True


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== QUEST HANDLER TEST ===")
    
    # Test data
    # test_char = {
    #     'level': 1,
    #     'active_quests': [],
    #     'completed_quests': [],
    #     'experience': 0,
    #     'gold': 100
    # }
    #
    # test_quests = {
    #     'first_quest': {
    #         'quest_id': 'first_quest',
    #         'title': 'First Steps',
    #         'description': 'Complete your first quest',
    #         'reward_xp': 50,
    #         'reward_gold': 25,
    #         'required_level': 1,
    #         'prerequisite': 'NONE'
    #     }
    # }
    #
    # try:
    #     accept_quest(test_char, 'first_quest', test_quests)
    #     print("Quest accepted!")
    # except QuestRequirementsNotMetError as e:
    #     print(f"Cannot accept: {e}")

