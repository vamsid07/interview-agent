from typing import List, Dict

class PersonaDetector:
    def __init__(self):
        self.current_persona = "Neutral"
        self.persona_history = []
        self.response_lengths = []
        self.engagement_score = 0.5
        
    def update_from_llm_analysis(self, analysis_json: Dict, response_text: str):
        if not analysis_json:
            return

        detected = analysis_json.get("detected_persona", "Neutral")
        self.current_persona = detected
        self.persona_history.append(detected)
        
        word_count = len(response_text.split())
        self.response_lengths.append(word_count)
        
        self._update_engagement_score(analysis_json)
        
    def _update_engagement_score(self, analysis: Dict):
        base_score = 0.5
        
        positive_personas = ["Professional", "Efficient", "Expert"]
        negative_personas = ["Evasive", "Confused", "Vague"]
        
        if self.current_persona in positive_personas:
            base_score += 0.3
        elif self.current_persona in negative_personas:
            base_score -= 0.2
            
        if len(self.response_lengths) > 0:
            avg_len = sum(self.response_lengths) / len(self.response_lengths)
            if 40 <= avg_len <= 150: 
                base_score += 0.1
        
        self.engagement_score = min(max(base_score, 0.1), 1.0)

    def get_engagement_score(self) -> float:
        return self.engagement_score
    
    def get_current_persona(self) -> str:
        return self.current_persona

    def get_stats(self) -> Dict:
        return {
            "current_persona": self.current_persona,
            "history_count": len(self.persona_history),
            "engagement": f"{self.engagement_score:.0%}"
        }