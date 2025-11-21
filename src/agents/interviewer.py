import google.generativeai as genai
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

sys.path.append(str(Path(__file__).parent.parent))

from agents.role_configs import QUESTION_BANKS, ROLE_CONFIGURATIONS
from prompts.system_prompts import get_interviewer_prompt
from utils.persona_detector import PersonaDetector

class InterviewAgent:
    def __init__(self, role: str, experience_level: str):
        self.role = role
        self.experience_level = experience_level
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.conversation_history: List[Dict] = []
        self.question_count = 0
        self.topics_covered = set()
        self.persona_detector = PersonaDetector()
        self.system_prompt = get_interviewer_prompt(role, experience_level)
        
    def start_interview(self) -> str:
        opening_message = f"""Hello! Thank you for joining this {self.role} interview today. I'm looking forward to learning more about your experience and skills.

This will be a conversational interview where I'll ask you questions about your background, experience, and how you approach different situations. Feel free to take your time with your responses.

Let's begin. {self._get_opening_question()}"""
        
        self.conversation_history.append({
            "role": "assistant",
            "content": opening_message
        })
        return opening_message
    
    def _get_opening_question(self) -> str:
        questions = QUESTION_BANKS.get(self.role, {}).get("opening", [])
        if questions:
            return questions[0]
        return "Tell me about yourself and your relevant experience."
    
    def generate_next_question(self, user_response: Optional[str] = None) -> str:
        if user_response:
            self.conversation_history.append({
                "role": "user",
                "content": user_response
            })
            
            persona = self.persona_detector.analyze_response(user_response, self.conversation_history)
            strategy = self.persona_detector.get_interaction_strategy(persona)
            
            should_follow_up = self._should_ask_follow_up(user_response, persona)
            
            if should_follow_up:
                return self._generate_follow_up(user_response, strategy)
        
        self.question_count += 1
        
        if self.question_count >= 6:
            return self._generate_closing()
        
        return self._generate_new_question()
    
    def _should_ask_follow_up(self, response: str, persona: str) -> bool:
        word_count = len(response.split())
        
        if persona == "efficient" and word_count > 40:
            return False
        
        if persona == "confused" or word_count < 25:
            return True
        
        uncertainty_markers = ["i'm not sure", "i don't know", "maybe"]
        if any(marker in response.lower() for marker in uncertainty_markers):
            return True
        
        return False
    
    def _generate_follow_up(self, user_response: str, strategy: Dict) -> str:
        conversation_text = self._format_conversation_for_prompt()
        
        prompt = f"""{self.system_prompt}

Conversation so far:
{conversation_text}

Based on the candidate's last response, generate a brief follow-up question to probe deeper or clarify.

Candidate's response: {user_response}

Strategy: {strategy['guidance']}

Keep the follow-up natural and conversational. Ask only ONE specific follow-up question."""
        
        response = self.model.generate_content(prompt)
        follow_up = response.text
        
        self.conversation_history.append({
            "role": "assistant",
            "content": follow_up
        })
        return follow_up
    
    def _generate_new_question(self) -> str:
        conversation_text = self._format_conversation_for_prompt()
        
        prompt = f"""{self.system_prompt}

Conversation so far:
{conversation_text}

Based on the conversation, ask the next appropriate interview question for a {self.role} position.

Current question count: {self.question_count}
Topics to avoid repeating: {', '.join(self.topics_covered)}

Generate ONE clear, relevant question that assesses the candidate's skills and experience."""
        
        response = self.model.generate_content(prompt)
        question = response.text
        
        self.conversation_history.append({
            "role": "assistant",
            "content": question
        })
        return question
    
    def _generate_closing(self) -> str:
        closing = """Thank you for your time today. That concludes our interview. 

Do you have any questions for me about the role or the company before we wrap up?"""
        
        self.conversation_history.append({
            "role": "assistant",
            "content": closing
        })
        return closing
    
    def end_interview(self) -> str:
        return "Thank you again for your time. We'll be in touch soon with next steps. Have a great day!"
    
    def _format_conversation_for_prompt(self) -> str:
        formatted = []
        for msg in self.conversation_history[-6:]:
            role_label = "Interviewer" if msg["role"] == "assistant" else "Candidate"
            formatted.append(f"{role_label}: {msg['content']}")
        return "\n\n".join(formatted)