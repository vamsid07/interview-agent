import google.generativeai as genai
import os
import sys
from pathlib import Path
from typing import List, Dict
import re

sys.path.append(str(Path(__file__).parent.parent))

from prompts.system_prompts import get_evaluation_prompt
from prompts.evaluation_rubrics import SCORING_CRITERIA, EXPERIENCE_LEVEL_EXPECTATIONS

class InterviewEvaluator:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def generate_final_feedback(self, conversation_history: List[Dict], role: str, experience_level: str) -> str:
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

Be specific and reference actual responses from the interview."""
        
        try:
            response = self.model.generate_content(enhanced_prompt)
            feedback = response.text
            
            return self._format_feedback_output(feedback, role, experience_level)
        except Exception as e:
            return self._generate_fallback_feedback(conversation_history, role, experience_level)
    
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
    
    def _generate_fallback_feedback(self, conversation_history: List[Dict], role: str, experience_level: str) -> str:
        candidate_responses = [msg['content'] for msg in conversation_history if msg['role'] == 'user']
        
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
            feedback += "Responses were generally brief. Consider providing more detailed examples and explanations in future interviews.\n"
        elif avg_response_length > 100:
            feedback += "Responses were detailed and thorough. Ensure key points are communicated clearly and concisely.\n"
        else:
            feedback += "Response length was appropriate, demonstrating good communication balance.\n"
        
        feedback += """
## Recommendations

1. Practice answering behavioral questions using the STAR method (Situation, Task, Action, Result)
2. Prepare specific examples from your experience that demonstrate key competencies
3. Focus on quantifiable achievements and concrete outcomes
4. Research common interview questions for your target role

Thank you for participating in this practice interview. Good luck with your future interviews!"""
        
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