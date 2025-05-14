## memory.py

class ChatMemory:
    def __init__(self):
        self.sessions = {}

    def get(self, session_id: str):
        """
        Retrieve the conversation history for a given session.
        If no history exists, return an empty list.
        """
        return self.sessions.get(session_id, [])

    def append(self, session_id: str, user_message: str, bot_message: str):
        """
        Append a new message pair (user_message, bot_message) to the conversation history.
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.sessions[session_id].append({
            'user': user_message,
            'bot': bot_message
        })
