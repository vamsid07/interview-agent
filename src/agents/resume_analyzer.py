import os
from typing import Dict, Any
from utils.api_client import RobustAPIClient
from prompts.system_prompts import get_resume_analysis_prompt

class ResumeAnalyzer:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        self.api_client = RobustAPIClient(api_key)

    def analyze(self, role: str, resume_text: str) -> Dict[str, Any]:
        if not resume_text:
            return {}
            
        prompt = get_resume_analysis_prompt(role, resume_text)
        result = self.api_client.generate_json_content(prompt)
        
        if not result:
            return {
                "candidate_name": "Candidate",
                "focus_areas": [
                    {"topic": "General Experience", "reason": "Resume analysis failed", "suggested_question": "Tell me about your background."}
                ]
            }
            
        return result