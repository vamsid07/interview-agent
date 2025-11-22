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
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        self.conversation_history: List[Dict] = []
        self.question_count = 0
        self.topics_covered = set()
        self.persona_detector = PersonaDetector()
        self.system_prompt = get_interviewer_prompt(role, experience_level)
        self.follow_up_count = 0
        self.max_follow_ups = 1
        self.asked_questions = set()
        
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
            question = questions[0]
            self.asked_questions.add(question.lower()[:50])
            return question
        return "Tell me about yourself and your relevant experience."
    
    def generate_next_question(self, user_response: Optional[str] = None) -> str:
        if not user_response:
            return self._generate_new_question()
        
        self.conversation_history.append({
            "role": "user",
            "content": user_response
        })
        
        persona = self.persona_detector.analyze_response(user_response, self.conversation_history)
        strategy = self.persona_detector.get_interaction_strategy(persona)
        
        is_repetitive = self._detect_repetition(user_response)
        
        if is_repetitive:
            return self._handle_repetitive_response()
        
        if self._should_ask_follow_up(user_response, persona):
            self.follow_up_count += 1
            return self._generate_follow_up(user_response, strategy, persona)
        
        self.question_count += 1
        self.follow_up_count = 0
        
        if self.question_count >= 6:
            return self._generate_closing()
        
        return self._generate_new_question()
    
    def _detect_repetition(self, response: str) -> bool:
        if len(self.conversation_history) < 4:
            return False
        
        recent_responses = [
            msg['content'].lower() 
            for msg in self.conversation_history[-6:] 
            if msg['role'] == 'user'
        ]
        
        if len(recent_responses) < 2:
            return False
        
        current_lower = response.lower()
        
        for prev_response in recent_responses[:-1]:
            if len(prev_response) > 100 and len(current_lower) > 100:
                similarity = self._calculate_similarity(prev_response, current_lower)
                if similarity > 0.7:
                    return True
        
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _handle_repetitive_response(self) -> str:
        redirection = """I notice you've shared similar information before. Let me ask you something different to explore other aspects of your experience.

Could you tell me about a specific challenge you faced and how you overcame it? Please focus on a particular situation rather than general experience."""
        
        self.conversation_history.append({
            "role": "assistant",
            "content": redirection
        })
        return redirection
    
    def _should_ask_follow_up(self, response: str, persona: str) -> bool:
        if self.follow_up_count >= self.max_follow_ups:
            return False
        
        word_count = len(response.split())
        
        if persona == "efficient" and word_count > 50:
            return False
        
        if persona == "chatty":
            return False
        
        if persona == "confused" or word_count < 30:
            return True
        
        uncertainty_markers = ["i'm not sure", "i don't know", "maybe", "i think maybe", "probably"]
        if any(marker in response.lower() for marker in uncertainty_markers):
            return True
        
        vague_responses = ["kind of", "sort of", "somewhat", "a bit"]
        if any(marker in response.lower() for marker in vague_responses) and word_count < 40:
            return True
        
        return False
    
    def _generate_follow_up(self, user_response: str, strategy: Dict, persona: str) -> str:
        conversation_text = self._format_conversation_for_prompt()
        
        persona_guidance = {
            "confused": "The candidate seems uncertain. Ask a clarifying question with an example to guide them.",
            "efficient": "The candidate is concise. Ask a brief follow-up only if critical information is missing.",
            "chatty": "Acknowledge their response and redirect to the core question.",
            "normal": "Ask a natural follow-up to explore deeper or get specific examples."
        }
        
        prompt = f"""{self.system_prompt}

Conversation so far:
{conversation_text}

The candidate just responded: "{user_response}"

Persona detected: {persona}
Guidance: {persona_guidance.get(persona, persona_guidance['normal'])}

Generate ONE brief, natural follow-up question. Do not repeat what they already said. Ask for specific examples, outcomes, or details they haven't mentioned. Keep it conversational."""
        
        try:
            response = self.model.generate_content(prompt)
            follow_up = response.text.strip()
            
            self.conversation_history.append({
                "role": "assistant",
                "content": follow_up
            })
            return follow_up
        except Exception as e:
            fallback = "Could you provide a specific example of that?"
            self.conversation_history.append({
                "role": "assistant",
                "content": fallback
            })
            return fallback
    
    def _generate_new_question(self) -> str:
        conversation_text = self._format_conversation_for_prompt()
        
        categories = QUESTION_BANKS.get(self.role, {}).keys()
        unused_categories = [cat for cat in categories if cat not in self.topics_covered and cat != "opening"]
        
        category_hint = ""
        if unused_categories:
            category_hint = f"Focus on: {unused_categories[0]}"
            self.topics_covered.add(unused_categories[0])
        
        prompt = f"""{self.system_prompt}

Conversation so far:
{conversation_text}

Interview progress: Question {self.question_count + 1} of 6
{category_hint}

IMPORTANT: Review the conversation above and ask a NEW question that has NOT been asked before. Do not repeat any previous questions. Generate a fresh, relevant question for {self.role} at {self.experience_level} level."""
        
        try:
            response = self.model.generate_content(prompt)
            question = response.text.strip()
            
            question_start = question.lower()[:50]
            
            if question_start in self.asked_questions:
                question = self._get_fallback_question()
            else:
                self.asked_questions.add(question_start)
            
            self.conversation_history.append({
                "role": "assistant",
                "content": question
            })
            return question
        except Exception as e:
            fallback = self._get_fallback_question()
            self.conversation_history.append({
                "role": "assistant",
                "content": fallback
            })
            return fallback
    
    def _get_fallback_question(self) -> str:
        fallbacks = {
            "Software Engineer": [
                "Tell me about a challenging technical problem you solved recently.",
                "How do you approach debugging a production issue?",
                "Describe a time you had to learn a new technology quickly.",
                "How do you handle code reviews and feedback?",
                "Tell me about a project you're particularly proud of."
            ],
            "Sales Representative": [
                "Describe your approach to handling objections from potential clients.",
                "Tell me about a time you lost a deal. What did you learn?",
                "How do you build rapport with new clients?",
                "Describe your typical sales process from lead to close.",
                "How do you stay motivated during slow periods?"
            ],
            "Retail Associate": [
                "How do you handle a situation where a customer is dissatisfied with a product?",
                "Tell me about a time you went above and beyond for a customer.",
                "How do you balance helping multiple customers at once?",
                "Describe a time you worked as part of a team.",
                "How do you handle stress during busy periods?"
            ]
        }
        
        available_fallbacks = [
            q for q in fallbacks.get(self.role, [])
            if q.lower()[:50] not in self.asked_questions
        ]
        
        if available_fallbacks:
            question = available_fallbacks[0]
            self.asked_questions.add(question.lower()[:50])
            return question
        
        return "What motivates you in your professional career?"
    
    def _generate_closing(self) -> str:
        closing = """Thank you for your thoughtful responses today. That concludes the main part of our interview.

Do you have any questions for me about the role, team, or company?"""
        
        self.conversation_history.append({
            "role": "assistant",
            "content": closing
        })
        return closing
    
    def end_interview(self) -> str:
        return "Thank you again for your time today. We appreciate you taking the time to speak with us. We'll be in touch soon with next steps. Have a great day!"
    
    def _format_conversation_for_prompt(self) -> str:
        formatted = []
        recent_messages = self.conversation_history[-8:]
        
        for msg in recent_messages:
            role_label = "Interviewer" if msg["role"] == "assistant" else "Candidate"
            formatted.append(f"{role_label}: {msg['content']}")
        
        return "\n\n".join(formatted)