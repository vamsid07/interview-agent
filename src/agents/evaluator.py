import google.generativeai as genai
import os
import sys
from pathlib import Path
from typing import List, Dict

sys.path.append(str(Path(__file__).parent.parent))

from prompts.system_prompts import get_evaluation_prompt

class InterviewEvaluator:
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def generate_final_feedback(self, conversation_history: List[Dict], role: str, experience_level: str) -> str:
        conversation_text = self._format_conversation(conversation_history)
        
        evaluation_prompt = get_evaluation_prompt(role, experience_level, conversation_text)
        
        response = self.model.generate_content(evaluation_prompt)
        
        return response.text
    
    def _format_conversation(self, conversation_history: List[Dict]) -> str:
        formatted = []
        for msg in conversation_history:
            role_label = "Interviewer" if msg["role"] == "assistant" else "Candidate"
            formatted.append(f"{role_label}: {msg['content']}")
        return "\n\n".join(formatted)
    
    def evaluate_response(self, question: str, answer: str) -> Dict:
        word_count = len(answer.split())
        
        flags = []
        if word_count < 20:
            flags.append("too_brief")
        elif word_count > 150:
            flags.append("too_verbose")
        
        uncertainty_markers = ["i'm not sure", "i don't know", "maybe", "probably"]
        if any(marker in answer.lower() for marker in uncertainty_markers):
            flags.append("uncertain")
        
        if word_count >= 40 and word_count <= 120 and not flags:
            flags.append("strong_answer")
        
        return {
            "word_count": word_count,
            "flags": flags,
            "needs_follow_up": "too_brief" in flags or "uncertain" in flags
        }