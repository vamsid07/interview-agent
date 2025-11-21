from typing import List, Dict

class PersonaDetector:
    def __init__(self):
        self.response_lengths = []
        self.uncertainty_count = 0
        self.off_topic_count = 0
        
    def analyze_response(self, response: str, conversation_history: List[Dict]) -> str:
        word_count = len(response.split())
        self.response_lengths.append(word_count)
        
        uncertainty_markers = ["i'm not sure", "i don't know", "maybe", "i think", "probably", "not certain"]
        has_uncertainty = any(marker in response.lower() for marker in uncertainty_markers)
        if has_uncertainty:
            self.uncertainty_count += 1
        
        if word_count < 20:
            return "efficient"
        
        if word_count > 150:
            return "chatty"
        
        if has_uncertainty and word_count < 30:
            return "confused"
        
        return "normal"
    
    def get_interaction_strategy(self, persona: str) -> Dict:
        strategies = {
            "confused": {
                "approach": "clarify",
                "guidance": "Provide examples and break down the question",
                "follow_up_threshold": "low"
            },
            "efficient": {
                "approach": "respect_pace",
                "guidance": "Move forward quickly if answer is complete",
                "follow_up_threshold": "high"
            },
            "chatty": {
                "approach": "redirect",
                "guidance": "Acknowledge input and gently refocus",
                "follow_up_threshold": "medium"
            },
            "normal": {
                "approach": "standard",
                "guidance": "Continue with normal interview flow",
                "follow_up_threshold": "medium"
            }
        }
        return strategies.get(persona, strategies["normal"])
    
    def reset(self):
        self.response_lengths = []
        self.uncertainty_count = 0
        self.off_topic_count = 0