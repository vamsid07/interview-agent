import os
import logging
from typing import List, Dict, Tuple, Optional
from agents.role_configs import QUESTION_BANKS
from prompts.system_prompts import get_interviewer_prompt, get_reasoning_prompt
from utils.persona_detector import PersonaDetector
from utils.response_validator import ResponseValidator
from utils.api_client import RobustAPIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterviewAgent:
    def __init__(self, role: str, experience_level: str, resume_text: str = "", interview_plan: Dict = None):
        self.role = role
        self.experience_level = experience_level
        self.resume_text = resume_text
        self.interview_plan = interview_plan or {}
        
        api_key = os.getenv("GROQ_API_KEY")
        self.api_client = RobustAPIClient(api_key)
        
        self.validator = ResponseValidator()
        self.persona_detector = PersonaDetector()
        
        self.conversation_history: List[Dict] = []
        self.question_count = 0
        self.topics_covered = set()
        self.last_brain_output = None
        self.focus_areas_covered = set()
        
        self.last_focus_topic = "your background"
        self.last_strategy = "OPENING"
        
    def start_interview(self) -> str:
        focus_areas = self.interview_plan.get("focus_areas", [])
        
        if focus_areas:
            first_topic = focus_areas[0]
            self.focus_areas_covered.add(first_topic['topic'])
            self.last_focus_topic = first_topic['topic']
            
            candidate_name = self.interview_plan.get('candidate_name', 'Candidate')
            if not candidate_name: candidate_name = "Candidate"
                
            opening = f"Hello {candidate_name}. I've reviewed your resume. I'm particularly interested in {first_topic['topic']} because {first_topic['reason']}. {first_topic['suggested_question']}"
        elif self.resume_text:
             opening = f"Hello! I've reviewed your resume. Let's start with a quick introduction. Walk me through your recent experience."
        else:
            opening = f"Hello! I'm an AI interviewer for the {self.role} position. Tell me about yourself."
        
        self.conversation_history.append({"role": "assistant", "content": opening})
        return opening
    
    def generate_next_question(self, user_response: str) -> Tuple[str, Optional[str]]:
        is_valid, error_msg = self.validator.validate_user_response(user_response)
        if not is_valid:
            return f"I didn't catch that. {error_msg}", "validation_error"
        
        sanitized_response = self.validator.sanitize_response(user_response)
        self.conversation_history.append({"role": "user", "content": sanitized_response})

        brain_output = self._run_reasoning_step(sanitized_response)
        self.last_brain_output = brain_output
        
        self.last_strategy = brain_output.get("strategy", "MOVE_ON")
        self.last_focus_topic = brain_output.get("next_focus", self.last_focus_topic)

        self.persona_detector.update_from_llm_analysis(brain_output, sanitized_response)

        next_question = self._generate_response_from_strategy(
            self.last_strategy, 
            self.last_focus_topic, 
            brain_output
        )
        
        self.conversation_history.append({"role": "assistant", "content": next_question})
        self.question_count += 1
        
        return next_question, None
    
    def _run_reasoning_step(self, last_response: str) -> Dict:
        history_text = self._format_conversation_limit(5)
        prompt = get_reasoning_prompt(self.role, self.experience_level, history_text, last_response, self.resume_text)
        result = self.api_client.generate_json_content(prompt)
        return result or {"strategy": "MOVE_ON", "reasoning": "System Fallback", "detected_persona": "Neutral", "next_focus": "experience"}

    def _generate_response_from_strategy(self, strategy: str, focus: str, analysis: Dict) -> str:
        focus_areas = self.interview_plan.get("focus_areas", [])
        
        system_prompt = get_interviewer_prompt(self.role, self.experience_level, self.resume_text, focus_areas)
        history_text = self._format_conversation_limit(5)
        
        action_instruction = ""
        if strategy == "DRILL_DOWN":
            action_instruction = f"User was vague. Drill down into {focus}. Demand specifics."
        elif strategy == "MOVE_ON":
            next_strategic_topic = self._get_next_strategic_topic()
            if next_strategic_topic:
                action_instruction = f"Move on. The Architect flagged '{next_strategic_topic['topic']}' as a concern ({next_strategic_topic['reason']}). Probe this now."
            else:
                topic = self._select_next_topic()
                action_instruction = f"Move on. Ask about {topic}."
        else:
            action_instruction = f"Strategy: {strategy}. Focus: {focus}."

        final_prompt = f"{system_prompt}\n\nHistory:\n{history_text}\n\nReasoning: {analysis.get('reasoning')}\nInstruction: {action_instruction}\nGenerate response:"
        response = self.api_client.generate_content(final_prompt)

        if not response:
            logger.warning("LLM Response failed. Using Context-Aware Fallback.")
            if strategy == "DRILL_DOWN":
                return f"Could you be more specific about {focus}? I'd like to hear a concrete example."
            elif strategy == "CLARIFY":
                return f"I'm not sure I understood that part about {focus}. Could you rephrase it?"
            else:
                return f"That's interesting. Let's shift gears. Tell me about your experience with {self._select_next_topic()}."
                
        return response

    def _get_next_strategic_topic(self) -> Optional[Dict]:
        focus_areas = self.interview_plan.get("focus_areas", [])
        for area in focus_areas:
            if area['topic'] not in self.focus_areas_covered:
                self.focus_areas_covered.add(area['topic'])
                return area
        return None

    def _select_next_topic(self) -> str:
        all_cats = QUESTION_BANKS.get(self.role, {}).keys()
        remaining = [c for c in all_cats if c not in self.topics_covered and c != "opening"]
        if remaining:
            topic = remaining[0]
            self.topics_covered.add(topic)
            return topic
        return "professional challenges"

    def _format_conversation_limit(self, limit: int) -> str:
        msgs = self.conversation_history[-limit*2:] 
        return "\n".join([f"{m['role'].upper()}: {m['content']}" for m in msgs])
    
    def get_total_questions(self) -> int:
        return self.question_count

    def get_latest_thought_process(self) -> Dict:
        return self.last_brain_output or {}
