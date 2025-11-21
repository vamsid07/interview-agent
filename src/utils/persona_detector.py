from typing import List, Dict

class PersonaDetector:
    def __init__(self):
        self.response_lengths = []
        self.uncertainty_count = 0
        self.off_topic_count = 0
        self.response_history = []
        
    def analyze_response(self, response: str, conversation_history: List[Dict]) -> str:
        word_count = len(response.split())
        self.response_lengths.append(word_count)
        self.response_history.append(response)
        
        uncertainty_markers = [
            "i'm not sure", "i don't know", "maybe", "i think", 
            "probably", "not certain", "unsure", "i guess"
        ]
        has_uncertainty = sum(1 for marker in uncertainty_markers if marker in response.lower())
        
        if has_uncertainty > 0:
            self.uncertainty_count += 1
        
        if len(self.response_history) < 2:
            if word_count < 20:
                return "efficient"
            elif word_count > 150:
                return "chatty"
            elif has_uncertainty > 1:
                return "confused"
            return "normal"
        
        avg_length = sum(self.response_lengths) / len(self.response_lengths)
        uncertainty_ratio = self.uncertainty_count / len(self.response_history)
        
        if uncertainty_ratio > 0.5 and avg_length < 40:
            return "confused"
        
        if avg_length < 30 and uncertainty_ratio < 0.3:
            return "efficient"
        
        if avg_length > 120:
            if self._is_rambling(response):
                return "chatty"
        
        return "normal"
    
    def _is_rambling(self, response: str) -> bool:
        sentences = [s.strip() for s in response.split('.') if s.strip()]
        
        if len(sentences) < 3:
            return False
        
        rambling_indicators = [
            "and also", "and then", "you know", "like i said",
            "basically", "actually", "so yeah", "i mean"
        ]
        
        indicator_count = sum(1 for indicator in rambling_indicators if indicator in response.lower())
        
        return indicator_count >= 3 or len(sentences) > 8
    
    def get_interaction_strategy(self, persona: str) -> Dict:
        strategies = {
            "confused": {
                "approach": "clarify_and_guide",
                "guidance": "Provide clear structure and examples. Break down complex questions into simpler parts.",
                "follow_up_threshold": "low",
                "question_style": "simplified",
                "encouragement_level": "high"
            },
            "efficient": {
                "approach": "respect_pace",
                "guidance": "Move forward efficiently. Avoid unnecessary probing if answers are complete.",
                "follow_up_threshold": "high",
                "question_style": "direct",
                "encouragement_level": "medium"
            },
            "chatty": {
                "approach": "redirect_focus",
                "guidance": "Acknowledge their input positively, then gently refocus on the core question.",
                "follow_up_threshold": "medium",
                "question_style": "focused",
                "encouragement_level": "medium"
            },
            "normal": {
                "approach": "standard_flow",
                "guidance": "Continue with normal interview flow. Adapt as needed.",
                "follow_up_threshold": "medium",
                "question_style": "conversational",
                "encouragement_level": "medium"
            }
        }
        return strategies.get(persona, strategies["normal"])
    
    def get_engagement_score(self) -> float:
        if not self.response_history:
            return 0.5
        
        avg_length = sum(self.response_lengths) / len(self.response_lengths)
        uncertainty_ratio = self.uncertainty_count / len(self.response_history)
        
        length_score = min(avg_length / 80, 1.0)
        certainty_score = 1.0 - uncertainty_ratio
        
        consistency_score = 1.0
        if len(self.response_lengths) > 2:
            variance = sum((x - avg_length) ** 2 for x in self.response_lengths) / len(self.response_lengths)
            std_dev = variance ** 0.5
            consistency_score = max(0, 1.0 - (std_dev / avg_length if avg_length > 0 else 0))
        
        engagement = (length_score * 0.4 + certainty_score * 0.4 + consistency_score * 0.2)
        return round(engagement, 2)
    
    def reset(self):
        self.response_lengths = []
        self.uncertainty_count = 0
        self.off_topic_count = 0
        self.response_history = []