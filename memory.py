# Here will code for memory storage

from collections import defaultdict


# session_memory = {
#   "admin-123": ["...messages..."],
#   "manager-456": ["...messages..."]
# }


session_memory = defaultdict(list)

def get_history(session_id : str) -> list[str]:

    """
    Gets the previous history (if available) using session ID
    """
    return session_memory[session_id]

def append_to_history(session_id : str, user_msg : str, bot_msg : str):
    
    """
    Add into the history after conversation
    """
    session_memory[session_id].append(f"User {user_msg}")
    session_memory[session_id].append(f"Assistant {bot_msg}")


def clear_history(session_id : str):
    
    """
    Clears the memory history using session ID
    """

    session_memory[session_id] = []







