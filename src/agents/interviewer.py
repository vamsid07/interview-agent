import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import Counter
import re
import logging

sys.path.append(str(Path(__file__).parent.parent))

from agents.role_configs import QUESTION_BANKS, ROLE_CONFIGURATIONS
from prompts.system_prompts import get_interviewer_prompt
from utils.persona_detector import PersonaDetector
from utils.response_validator import ResponseValidator
from utils.api_client import RobustAPIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterviewAgent:
    def __init__(self, role: str, experience_level: str):
        self.role = role
        self.experience_level = experience_level
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.api_client = RobustAPIClient(api_key)
        self.validator = ResponseValidator()
        
        self.conversation_history: List[Dict] = []
        self.question_count = 0
        self.topics_covered = set()
        self.persona_detector = PersonaDetector()
        self.system_prompt = get_interviewer_prompt(role, experience_level)
        self.consecutive_follow_ups = 0
        self.asked_questions = set()
        self.weak_areas = []
        self.strong_areas = []
        self.response_quality_scores = []
        self.error_count = 0
        
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
    
    def generate_next_question(self, user_response: Optional[str] = None) -> Tuple[str, Optional[str]]:
        if not user_response:
            return self._generate_new_question()
        
        is_valid, error_message = self.validator.validate_user_response(user_response)
        if not is_valid:
            logger.warning(f"Invalid user response: {error_message}")
            return self._handle_invalid_response(error_message), "validation_error"
        
        sanitized_response = self.validator.sanitize_response(user_response)
        
        self.conversation_history.append({
            "role": "user",
            "content": sanitized_response
        })
        
        quality_score = self._assess_response_quality(sanitized_response)
        self.response_quality_scores.append(quality_score)
        
        persona = self.persona_detector.analyze_response(sanitized_response, self.conversation_history)
        strategy = self.persona_detector.get_interaction_strategy(persona)
        
        is_repetitive = self._detect_repetition(sanitized_response)
        
        if is_repetitive:
            return self._handle_repetitive_response(), None
        
        should_follow_up, reason = self._should_ask_follow_up(sanitized_response, persona, quality_score)
        
        if should_follow_up:
            self.consecutive_follow_ups += 1
            return self._generate_follow_up(sanitized_response, strategy, persona, reason)
        
        self.question_count += 1
        self.consecutive_follow_ups = 0
        
        if self._should_end_interview():
            return self._generate_closing(), None
        
        return self._generate_new_question()
    
    def _handle_invalid_response(self, error_message: str) -> str:
        response = f"""I noticed an issue with your response: {error_message}

Please try again and provide a thoughtful, professional answer to the question."""
        
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        return response
    
    def _assess_response_quality(self, response: str) -> Dict:
        word_count = len(response.split())
        sentence_count = len([s for s in response.split('.') if s.strip()])
        
        score = 5
        flags = []
        
        if word_count < 20:
            flags.append("too_brief")
            score = 3
        elif word_count > 150:
            flags.append("verbose")
            score = 6
        
        uncertainty_markers = ["i'm not sure", "i don't know", "maybe", "i think maybe", "probably", "not certain"]
        uncertainty_count = sum(1 for marker in uncertainty_markers if marker in response.lower())
        
        if uncertainty_count > 2:
            flags.append("very_uncertain")
            score -= 2
        elif uncertainty_count > 0:
            flags.append("uncertain")
            score -= 1
        
        specific_markers = ["for example", "specifically", "i implemented", "i developed", "i achieved", "i led", "resulted in", "outcome was"]
        if any(marker in response.lower() for marker in specific_markers):
            flags.append("specific")
            score += 2
        
        if self._contains_structured_answer(response):
            flags.append("structured")
            score += 1
        
        vague_markers = ["kind of", "sort of", "basically", "just", "you know", "like"]
        vague_count = sum(1 for marker in vague_markers if marker in response.lower())
        if vague_count > 3:
            flags.append("vague")
            score -= 1
        
        return {
            "score": min(max(score, 1), 10),
            "word_count": word_count,
            "flags": flags,
            "needs_clarification": "too_brief" in flags or "very_uncertain" in flags or "vague" in flags
        }
    
    def _contains_structured_answer(self, answer: str) -> bool:
        answer_lower = answer.lower()
        
        structure_indicators = {
            "situation": ["situation", "context", "scenario", "at the time", "when i was"],
            "task": ["task", "responsibility", "needed to", "had to", "my role"],
            "action": ["i did", "i implemented", "i developed", "my approach", "i decided"],
            "result": ["result", "outcome", "achieved", "improved", "increased", "decreased"]
        }
        
        matches = 0
        for category, indicators in structure_indicators.items():
            if any(indicator in answer_lower for indicator in indicators):
                matches += 1
        
        return matches >= 3
    
    def _should_end_interview(self) -> bool:
        if self.question_count < 4:
            return False
        
        if self.question_count >= 10:
            return True
        
        if len(self.response_quality_scores) < 3:
            return False
        
        recent_scores = [s["score"] for s in self.response_quality_scores[-3:]]
        avg_recent = sum(recent_scores) / len(recent_scores)
        
        overall_scores = [s["score"] for s in self.response_quality_scores]
        avg_overall = sum(overall_scores) / len(overall_scores)
        
        if self.question_count >= 8 and avg_overall >= 7:
            return True
        
        if self.question_count >= 6:
            categories = QUESTION_BANKS.get(self.role, {}).keys()
            core_categories = [cat for cat in categories if cat != "opening"]
            if len(self.topics_covered) >= len(core_categories):
                return True
        
        return False
    
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
        current_normalized = self._normalize_text(current_lower)
        current_key_phrases = self._extract_key_phrases(current_normalized)
        
        for prev_response in recent_responses[:-1]:
            prev_normalized = self._normalize_text(prev_response)
            prev_key_phrases = self._extract_key_phrases(prev_normalized)
            
            if len(prev_response) > 100 and len(current_lower) > 100:
                lexical_sim = self._calculate_similarity(prev_response, current_lower)
                semantic_sim = self._calculate_phrase_overlap(current_key_phrases, prev_key_phrases)
                
                if lexical_sim > 0.7 or semantic_sim > 0.65:
                    return True
        
        return False
    
    def _normalize_text(self, text: str) -> str:
        text = re.sub(r'[^\w\s]', '', text)
        stopwords = {'i', 'me', 'my', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        words = [w for w in text.split() if w not in stopwords and len(w) > 2]
        return ' '.join(words)
    
    def _extract_key_phrases(self, text: str) -> set:
        words = text.split()
        phrases = set()
        
        for i in range(len(words)):
            if i + 1 < len(words):
                phrases.add(f"{words[i]} {words[i+1]}")
            if i + 2 < len(words):
                phrases.add(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        return phrases
    
    def _calculate_phrase_overlap(self, phrases1: set, phrases2: set) -> float:
        if not phrases1 or not phrases2:
            return 0.0
        
        intersection = phrases1.intersection(phrases2)
        union = phrases1.union(phrases2)
        
        return len(intersection) / len(union) if union else 0.0
    
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
    
    def _should_ask_follow_up(self, response: str, persona: str, quality_score: Dict) -> tuple:
        if self.consecutive_follow_ups >= 2:
            return False, None
        
        word_count = quality_score["word_count"]
        score = quality_score["score"]
        
        if quality_score["needs_clarification"]:
            return True, "clarification_needed"
        
        if persona == "confused":
            return True, "guide_confused"
        
        if score < 5:
            return True, "improve_quality"
        
        if persona == "efficient" and word_count > 60 and score >= 7:
            return False, None
        
        if persona == "chatty" and word_count > 120:
            return False, None
        
        if "specific" not in quality_score["flags"] and word_count < 80:
            return True, "request_specifics"
        
        return False, None
    
    def _generate_follow_up(self, user_response: str, strategy: Dict, persona: str, reason: str) -> Tuple[str, Optional[str]]:
        conversation_text = self._format_conversation_for_prompt()
        
        follow_up_strategies = {
            "clarification_needed": "The response was too brief or vague. Ask for clarification or more details.",
            "guide_confused": "The candidate seems uncertain. Provide a specific example or guide them.",
            "improve_quality": "The response lacked depth. Ask for specific examples or concrete details.",
            "request_specifics": "The response was general. Request a specific situation or measurable outcome."
        }
        
        prompt = f"""{self.system_prompt}

Conversation so far:
{conversation_text}

The candidate just responded: "{user_response}"

Persona detected: {persona}
Follow-up reason: {follow_up_strategies.get(reason, 'Request more detail')}

Generate ONE brief, natural follow-up question. Ask for specific examples, concrete outcomes, or missing details. Keep it conversational and supportive."""
        
        follow_up = self.api_client.generate_content(prompt)
        
        if not follow_up:
            logger.error("API failed to generate follow-up")
            self.error_count += 1
            fallback = self._get_fallback_followup(reason)
            self.conversation_history.append({
                "role": "assistant",
                "content": fallback
            })
            return fallback, "api_error"
        
        is_valid, error_msg = self.validator.validate_llm_question(follow_up)
        if not is_valid:
            logger.warning(f"Invalid LLM question: {error_msg}")
            self.error_count += 1
            fallback = self._get_fallback_followup(reason)
            self.conversation_history.append({
                "role": "assistant",
                "content": fallback
            })
            return fallback, "validation_error"
        
        self.conversation_history.append({
            "role": "assistant",
            "content": follow_up
        })
        return follow_up, None
    
    def _get_fallback_followup(self, reason: str) -> str:
        fallbacks = {
            "clarification_needed": "Could you elaborate on that a bit more?",
            "guide_confused": "Let me ask it differently - can you give me a specific example from your experience?",
            "improve_quality": "What were the specific outcomes or results from that situation?",
            "request_specifics": "Could you walk me through a concrete example of that?"
        }
        return fallbacks.get(reason, "Could you provide more details about that?")
    
    def _generate_new_question(self) -> Tuple[str, Optional[str]]:
        conversation_text = self._format_conversation_for_prompt()
        
        target_category = self._select_next_category()
        
        prompt = f"""{self.system_prompt}

Conversation so far:
{conversation_text}

Interview progress: Question {self.question_count + 1}
Focus area: {target_category}

Generate a NEW question that:
1. Has NOT been asked before in this conversation
2. Explores {target_category} for {self.role} at {self.experience_level} level
3. Is relevant and natural given the conversation flow
4. Assesses specific competencies for this role

Ask ONE clear, focused question."""
        
        question = self.api_client.generate_content(prompt)
        
        if not question:
            logger.error("API failed to generate question")
            self.error_count += 1
            fallback = self._get_fallback_question()
            self.conversation_history.append({
                "role": "assistant",
                "content": fallback
            })
            return fallback, "api_error"
        
        is_valid, error_msg = self.validator.validate_llm_question(question)
        if not is_valid:
            logger.warning(f"Invalid LLM question: {error_msg}, using fallback")
            self.error_count += 1
            fallback = self._get_fallback_question()
            self.conversation_history.append({
                "role": "assistant",
                "content": fallback
            })
            return fallback, "validation_error"
        
        question_start = question.lower()[:50]
        
        if question_start in self.asked_questions:
            logger.info("Question already asked, using fallback")
            question = self._get_fallback_question()
        else:
            self.asked_questions.add(question_start)
        
        self.conversation_history.append({
            "role": "assistant",
            "content": question
        })
        return question, None
    
    def _select_next_category(self) -> str:
        categories = QUESTION_BANKS.get(self.role, {}).keys()
        unused_categories = [cat for cat in categories if cat not in self.topics_covered and cat != "opening"]
        
        if unused_categories:
            selected = unused_categories[0]
            self.topics_covered.add(selected)
            return selected
        
        if len(self.response_quality_scores) >= 2:
            weak_responses = [i for i, s in enumerate(self.response_quality_scores) if s["score"] < 6]
            if weak_responses:
                return "behavioral"
        
        all_categories = [cat for cat in categories if cat != "opening"]
        if all_categories:
            return all_categories[self.question_count % len(all_categories)]
        
        return "general"
    
    def _get_fallback_question(self) -> str:
        fallbacks = {
            "Software Engineer": [
                "Tell me about a challenging technical problem you solved recently.",
                "How do you approach debugging a production issue?",
                "Describe a time you had to learn a new technology quickly.",
                "How do you handle code reviews and feedback?",
                "Tell me about a project you're particularly proud of.",
                "Walk me through your approach to system design.",
                "How do you ensure code quality in your projects?",
                "Describe a time you optimized performance in an application."
            ],
            "Sales Representative": [
                "Describe your approach to handling objections from potential clients.",
                "Tell me about a time you lost a deal. What did you learn?",
                "How do you build rapport with new clients?",
                "Describe your typical sales process from lead to close.",
                "How do you stay motivated during slow periods?",
                "Tell me about your biggest sales win.",
                "How do you prioritize your sales pipeline?",
                "Describe a time you turned a no into a yes."
            ],
            "Retail Associate": [
                "How do you handle a situation where a customer is dissatisfied with a product?",
                "Tell me about a time you went above and beyond for a customer.",
                "How do you balance helping multiple customers at once?",
                "Describe a time you worked as part of a team.",
                "How do you handle stress during busy periods?",
                "Tell me about a difficult customer interaction.",
                "How do you stay motivated during slow shifts?",
                "Describe your approach to upselling or cross-selling."
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
        recent_messages = self.conversation_history[-10:]
        
        for msg in recent_messages:
            role_label = "Interviewer" if msg["role"] == "assistant" else "Candidate"
            formatted.append(f"{role_label}: {msg['content']}")
        
        return "\n\n".join(formatted)
    
    def get_total_questions(self) -> int:
        return self.question_count
    
    def get_error_stats(self) -> Dict:
        return {
            'total_errors': self.error_count,
            'api_stats': self.api_client.get_stats()
        }