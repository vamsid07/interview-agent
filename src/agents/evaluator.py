import os
import logging
from typing import List, Dict, Any
from prompts.system_prompts import get_robust_evaluation_prompt
from utils.api_client import RobustAPIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterviewEvaluator:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        self.api_client = RobustAPIClient(api_key)
    
    def generate_comprehensive_report(self, conversation_history: List[Dict], role: str, level: str, interview_plan: Dict = None) -> Dict[str, Any]:
        conversation_text = self._format_conversation(conversation_history)
        prompt = get_robust_evaluation_prompt(role, level, conversation_text, interview_plan)
        
        result = self.api_client.generate_json_content(prompt)
        
        if not result:
            return self._generate_fallback_report()
            
        return result

    def _format_conversation(self, history: List[Dict]) -> str:
        return "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in history])
    
    def _generate_fallback_report(self) -> Dict[str, Any]:
        return {
            "scores": {"technical_depth": 50, "communication_clarity": 50, "problem_solving": 50, "culture_fit": 50, "consistency": 50},
            "feedback": {"strengths": ["Completed interview"], "weaknesses": ["Could not generate detailed analysis"], "coach_tips": ["Try again"]},
            "evidence": [],
            "hiring_decision": "N/A",
            "executive_summary": "Analysis failed due to API constraints."
        }
        
    def generate_final_feedback(self, conversation_history: List[Dict], role: str, experience_level: str) -> str:
        report = self.generate_comprehensive_report(conversation_history, role, experience_level)
        return f"Analysis Complete. Decision: {report.get('hiring_decision', 'N/A')}"