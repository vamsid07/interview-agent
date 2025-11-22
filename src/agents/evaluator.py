import os
import sys
from pathlib import Path
from typing import List, Dict
import re
import logging

sys.path.append(str(Path(__file__).parent.parent))

from prompts.system_prompts import get_evaluation_prompt
from prompts.evaluation_rubrics import SCORING_CRITERIA, EXPERIENCE_LEVEL_EXPECTATIONS
from utils.api_client import RobustAPIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterviewEvaluator:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.api_client = RobustAPIClient(api_key)
    
    def generate_final_feedback(self, conversation_history: List[Dict], role: str, experience_level: str) -> str:
        if not conversation_history or len(conversation_history) < 2:
            return self._generate_minimal_feedback(role, experience_level)
        
        conversation_text = self._format_conversation(conversation_history)
        
        evaluation_prompt = get_evaluation_prompt(role, experience_level, conversation_text)
        
        criteria = SCORING_CRITERIA.get(role, {})
        expectations = EXPERIENCE_LEVEL_EXPECTATIONS.get(experience_level, {})
        
        enhanced_prompt = f"""{evaluation_prompt}

Use these specific scoring criteria for {role}:
{self._format_criteria(criteria)}

Expected performance level for {experience_level}:
{self._format_expectations(expectations)}

Provide a structured evaluation with:
1. Overall Assessment (2-3 sentences)
2. Detailed Scores for each dimension (with justification)
3. Key Strengths (3-4 specific examples from conversation)
4. Areas for Improvement (3-4 specific, actionable items)
5. Next Steps (concrete recommendations)

Be specific and reference actual responses from the interview. Use a professional, constructive tone."""
        
        feedback = self.api_client.generate_content(enhanced_prompt)
        
        if not feedback:
            logger.error("API failed to generate feedback, using fallback")
            return self._generate_fallback_feedback(conversation_history, role, experience_level)
        
        if not self._validate_feedback_structure(feedback):
            logger.warning("Generated feedback lacks proper structure, enhancing")
            feedback = self._enhance_feedback_structure(feedback, role, experience_level)
        
        return self._format_feedback_output(feedback, role, experience_level)
    
    def _validate_feedback_structure(self, feedback: str) -> bool:
        required_sections = ['assessment', 'strength', 'improvement', 'recommendation']
        feedback_lower = feedback.lower()
        
        found_sections = sum(1 for section in required_sections if section in feedback_lower)
        
        return found_sections >= 3
    
    def _enhance_feedback_structure(self, feedback: str, role: str, experience_level: str) -> str:
        if len(feedback) < 100:
            return self._generate_fallback_feedback([], role, experience_level)
        
        enhanced = f"""## Overall Assessment

{feedback[:300]}

## Key Recommendations

Based on this interview, focus on:
1. Providing specific examples with measurable outcomes
2. Using the STAR method (Situation, Task, Action, Result) in your responses
3. Demonstrating deeper knowledge of {role} competencies
4. Practicing clear and concise communication

Continue preparing for interviews by researching common questions for {experience_level} level {role} positions."""
        
        return enhanced
    
    def _format_criteria(self, criteria: Dict) -> str:
        formatted = []
        for dimension, details in criteria.items():
            weight = details.get('weight', 0) * 100
            indicators = ', '.join(details.get('indicators', []))
            formatted.append(f"- {dimension.replace('_', ' ').title()} ({weight}%): {indicators}")
        return '\n'.join(formatted)
    
    def _format_expectations(self, expectations: Dict) -> str:
        formatted = []
        for dimension, score in expectations.items():
            formatted.append(f"- {dimension.replace('_', ' ').title()}: {score}/10")
        return '\n'.join(formatted)
    
    def _format_feedback_output(self, feedback: str, role: str, experience_level: str) -> str:
        header = f"""# Interview Feedback Report

**Role:** {role}
**Experience Level:** {experience_level}
**Date:** {self._get_current_date()}

---

"""
        return header + feedback
    
    def _get_current_date(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%B %d, %Y")
    
    def _generate_minimal_feedback(self, role: str, experience_level: str) -> str:
        return f"""# Interview Feedback Report

**Role:** {role}
**Experience Level:** {experience_level}

## Assessment

The interview session was too brief to provide comprehensive feedback. To get meaningful evaluation:

1. Answer at least 4-5 questions with detailed responses
2. Provide specific examples from your experience
3. Take time to think through your answers
4. Complete the full interview session

Please start a new interview and engage more fully with the questions."""
    
    def _generate_fallback_feedback(self, conversation_history: List[Dict], role: str, experience_level: str) -> str:
        candidate_responses = [msg['content'] for msg in conversation_history if msg['role'] == 'user']
        
        if not candidate_responses:
            return self._generate_minimal_feedback(role, experience_level)
        
        total_words = sum(len(response.split()) for response in candidate_responses)
        avg_response_length = total_words // len(candidate_responses) if candidate_responses else 0
        
        feedback = f"""# Interview Feedback Report

**Role:** {role}
**Experience Level:** {experience_level}

## Overall Assessment

The candidate provided {len(candidate_responses)} responses during the interview with an average response length of {avg_response_length} words. 

## Communication Style

"""
        
        if avg_response_length < 30:
            feedback += """Your responses were generally brief. Consider providing more detailed examples and explanations in future interviews. Aim for 50-100 words per response to demonstrate depth of knowledge and experience.

"""
        elif avg_response_length > 100:
            feedback += """Your responses were detailed and thorough. Ensure key points are communicated clearly and concisely without unnecessary elaboration. Balance depth with brevity.

"""
        else:
            feedback += """Response length was appropriate, demonstrating good communication balance. You provided enough detail without being overly verbose.

"""
        
        feedback += """## Key Recommendations

1. **Use the STAR Method**: Structure behavioral answers with Situation, Task, Action, and Result
2. **Provide Specific Examples**: Back up claims with concrete examples from your experience
3. **Quantify Achievements**: Include numbers, percentages, or measurable outcomes where possible
4. **Practice Common Questions**: Research and prepare for typical interview questions for your target role
5. **Ask Clarifying Questions**: If unsure about a question, ask for clarification rather than guessing

## Next Steps

- Review common interview questions for {role} positions at the {experience_level} level
- Prepare 5-7 strong examples from your experience that demonstrate key competencies
- Practice articulating your thoughts clearly and concisely
- Research the companies and roles you're targeting
- Consider doing mock interviews with peers or mentors

Thank you for participating in this practice interview. With preparation and practice, you'll be well-equipped for real interviews."""
        
        return feedback
    
    def _format_conversation(self, conversation_history: List[Dict]) -> str:
        formatted = []
        for msg in conversation_history:
            role_label = "Interviewer" if msg["role"] == "assistant" else "Candidate"
            formatted.append(f"{role_label}: {msg['content']}")
        return "\n\n".join(formatted)
    
    def evaluate_response(self, question: str, answer: str, role: str) -> Dict:
        word_count = len(answer.split())
        sentence_count = len([s for s in answer.split('.') if s.strip()])
        
        flags = []
        score = 5
        
        if word_count < 20:
            flags.append("too_brief")
            score = 3
        elif word_count > 150:
            flags.append("too_verbose")
            score = 6
        
        uncertainty_markers = ["i'm not sure", "i don't know", "maybe", "probably", "i think"]
        uncertainty_count = sum(1 for marker in uncertainty_markers if marker in answer.lower())
        
        if uncertainty_count > 2:
            flags.append("very_uncertain")
            score -= 2
        elif uncertainty_count > 0:
            flags.append("uncertain")
            score -= 1
        
        if self._contains_star_method(answer):
            flags.append("structured_answer")
            score += 2
        
        if word_count >= 40 and word_count <= 120 and not any(f in flags for f in ["uncertain", "very_uncertain"]):
            flags.append("strong_answer")
            score += 1
        
        specific_markers = ["for example", "specifically", "i implemented", "i developed", "i achieved"]
        if any(marker in answer.lower() for marker in specific_markers):
            flags.append("specific_examples")
            score += 1
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "flags": flags,
            "score": min(max(score, 1), 10),
            "needs_follow_up": "too_brief" in flags or "very_uncertain" in flags
        }
    
    def _contains_star_method(self, answer: str) -> bool:
        answer_lower = answer.lower()
        
        star_indicators = {
            "situation": ["situation", "context", "scenario", "at the time", "when i was"],
            "task": ["task", "responsibility", "needed to", "had to", "my role"],
            "action": ["i did", "i implemented", "i developed", "my approach", "i decided"],
            "result": ["result", "outcome", "achieved", "improved", "increased", "decreased"]
        }
        
        matches = 0
        for category, indicators in star_indicators.items():
            if any(indicator in answer_lower for indicator in indicators):
                matches += 1
        
        return matches >= 3