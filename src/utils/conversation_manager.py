import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class ConversationManager:
    def __init__(self):
        self.conversation_history: List[Dict] = []
        self.session_id: Optional[str] = None
        self.metadata: Dict = {}
        
    def initialize_conversation(self, role: str, experience_level: str) -> str:
        self.session_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.metadata = {
            "role": role,
            "experience_level": experience_level,
            "start_time": datetime.now().isoformat(),
            "status": "active"
        }
        self.conversation_history = []
        return self.session_id
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        if metadata:
            message["metadata"] = metadata
        self.conversation_history.append(message)
    
    def get_conversation_context(self) -> List[Dict]:
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.conversation_history
        ]
    
    def save_conversation(self):
        if not self.session_id:
            return
        
        os.makedirs("data/conversation_logs", exist_ok=True)
        filepath = f"data/conversation_logs/{self.session_id}.json"
        
        data = {
            "session_id": self.session_id,
            "metadata": self.metadata,
            "conversation": self.conversation_history
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    
    def load_conversation(self, session_id: str) -> bool:
        filepath = f"data/conversation_logs/{session_id}.json"
        
        if not os.path.exists(filepath):
            return False
        
        with open(filepath, "r") as f:
            data = json.load(f)
        
        self.session_id = data["session_id"]
        self.metadata = data["metadata"]
        self.conversation_history = data["conversation"]
        return True
    
    def get_formatted_transcript(self) -> str:
        transcript = []
        transcript.append(f"Interview Session: {self.session_id}")
        transcript.append(f"Role: {self.metadata.get('role', 'N/A')}")
        transcript.append(f"Level: {self.metadata.get('experience_level', 'N/A')}")
        transcript.append("\n" + "="*50 + "\n")
        
        for msg in self.conversation_history:
            role_label = "Interviewer" if msg["role"] == "assistant" else "Candidate"
            transcript.append(f"{role_label}: {msg['content']}\n")
        
        return "\n".join(transcript)