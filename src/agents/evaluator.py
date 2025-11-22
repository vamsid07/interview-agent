import os
import logging
import re
import json
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
        
        if result:
            return result
        
        logger.warning("JSON Evaluation failed. Attempting text-based degradation.")
        text_response = self.api_client.generate_content(prompt + "\n\nProvide the report in plain text.")
        
        if text_response:
            return self._graceful_degradation(text_response)
            
        return self._generate_fallback_report()

    def _graceful_degradation(self, text: str) -> Dict[str, Any]:
        """Extracts scores from unstructured text if JSON parsing fails."""
        fallback = self._generate_fallback_report()
        fallback["executive_summary"] = text[:500] + "..." 

        patterns = {
            "technical_depth": r"Technical.*?:?\s*(\d+)/100",
            "communication_clarity": r"Communication.*?:?\s*(\d+)/100",
            "problem_solving": r"Problem Solving.*?:?\s*(\d+)/100",
            "culture_fit": r"Culture.*?:?\s*(\d+)/100"
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fallback["scores"][key] = int(match.group(1))
                
        return fallback

    def _format_conversation(self, history: List[Dict]) -> str:
        return "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in history])
    
    def _generate_fallback_report(self) -> Dict[str, Any]:
        return {
            "scores": {"technical_depth": 50, "communication_clarity": 50, "problem_solving": 50, "culture_fit": 50, "consistency": 50},
            "feedback": {"strengths": ["Completed interview"], "weaknesses": ["Could not generate detailed analysis"], "coach_tips": ["Try again"]},
            "evidence": [],
            "hiring_decision": "Pending Review",
            "executive_summary": "The AI could not generate a structured report. Please review the transcript manually."
        }
        
    def generate_final_feedback(self, conversation_history: List[Dict], role: str, experience_level: str) -> str:
        report = self.generate_comprehensive_report(conversation_history, role, experience_level)
        return f"Analysis Complete. Decision: {report.get('hiring_decision', 'N/A')}"
