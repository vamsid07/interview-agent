from typing import List, Dict, Optional, Tuple
import random
from models.competency_model import CompetencyModel, SkillLevel

class QuestionSelector:
    def __init__(self, competency_model: CompetencyModel):
        self.competency_model = competency_model
        self.question_history: List[Dict] = []
        self.competency_question_count: Dict[str, int] = {}
        
    def select_next_question(self, conversation_history: List[Dict]) -> Tuple[str, str, Dict]:
        if len(conversation_history) == 0:
            return self._select_opening_question()
        
        unassessed = self.competency_model.get_unassessed_competencies()
        if unassessed:
            target_competency = self._prioritize_unassessed(unassessed)
            return self._generate_question_for_competency(target_competency, "initial_assessment")
        
        weak_areas = self.competency_model.get_weak_competencies()
        if weak_areas:
            target_competency = self._prioritize_weak_areas(weak_areas)
            return self._generate_question_for_competency(target_competency, "probe_weakness")
        
        gap_analysis = self.competency_model.get_competency_gap_analysis()
        if gap_analysis:
            highest_priority = list(gap_analysis.keys())[0]
            return self._generate_question_for_competency(highest_priority, "validate_assessment")
        
        least_covered = self._get_least_covered_competency()
        return self._generate_question_for_competency(least_covered, "comprehensive_coverage")
    
    def _select_opening_question(self) -> Tuple[str, str, Dict]:
        role = self.competency_model.role
        
        opening_questions = {
            "Software Engineer": [
                ("Tell me about your background as a software engineer and what areas you specialize in.", "technical_depth"),
                ("Walk me through a recent project you worked on and your specific contributions.", "technical_depth"),
                ("What interests you most about software development, and how did you get started in this field?", "learning_adaptability")
            ],
            "Sales Representative": [
                ("Tell me about your sales experience and the types of products or services you've sold.", "sales_methodology"),
                ("Describe your typical sales approach from first contact to closing a deal.", "sales_methodology"),
                ("What motivates you in sales, and what do you consider your biggest strength?", "resilience")
            ],
            "Retail Associate": [
                ("Tell me about your customer service experience and what you enjoy most about working with customers.", "customer_service"),
                ("Describe a typical day in your most recent retail position.", "customer_service"),
                ("What do you think makes excellent customer service, and how do you deliver it?", "customer_service")
            ]
        }
        
        questions = opening_questions.get(role, [("Tell me about your relevant experience.", "general")])
        question, competency = random.choice(questions)
        
        metadata = {
            "question_type": "opening",
            "target_competency": competency,
            "difficulty": "easy",
            "intent": "establish_baseline"
        }
        
        self.question_history.append({
            "question": question,
            "competency": competency,
            "metadata": metadata
        })
        
        return question, competency, metadata
    
    def _prioritize_unassessed(self, unassessed: List[str]) -> str:
        for competency in unassessed:
            if competency not in self.competency_question_count:
                return competency
        
        sorted_by_weight = sorted(
            unassessed,
            key=lambda c: self.competency_model.competencies[c].weight,
            reverse=True
        )
        return sorted_by_weight[0]
    
    def _prioritize_weak_areas(self, weak_areas: List[str]) -> str:
        least_questioned = None
        min_count = float('inf')
        
        for area in weak_areas:
            count = self.competency_question_count.get(area, 0)
            if count < min_count:
                min_count = count
                least_questioned = area
        
        return least_questioned if least_questioned else weak_areas[0]
    
    def _get_least_covered_competency(self) -> str:
        return min(
            self.competency_model.competencies.keys(),
            key=lambda c: self.competency_question_count.get(c, 0)
        )
    
    def _generate_question_for_competency(self, competency: str, intent: str) -> Tuple[str, str, Dict]:
        comp_obj = self.competency_model.competencies[competency]
        
        self.competency_question_count[competency] = self.competency_question_count.get(competency, 0) + 1
        
        difficulty = self._determine_difficulty(competency, intent)
        
        metadata = {
            "question_type": "targeted",
            "target_competency": competency,
            "difficulty": difficulty,
            "intent": intent,
            "target_skills": list(comp_obj.skills.keys())
        }
        
        question_prompt = self._build_question_generation_prompt(competency, comp_obj, difficulty, intent)
        
        return question_prompt, competency, metadata
    
    def _determine_difficulty(self, competency: str, intent: str) -> str:
        experience_level = self.competency_model.experience_level
        
        if intent == "initial_assessment":
            if experience_level == "Entry":
                return "easy"
            elif experience_level == "Mid":
                return "medium"
            else:
                return "medium"
        
        elif intent == "probe_weakness":
            return "medium"
        
        elif intent == "validate_assessment":
            comp = self.competency_model.competencies[competency]
            if comp.current_assessment and comp.current_assessment.value >= comp.target_level.value:
                return "hard"
            else:
                return "medium"
        
        return "medium"
    
    def _build_question_generation_prompt(self, competency: str, comp_obj, difficulty: str, intent: str) -> str:
        skills_list = ", ".join([s.name for s in comp_obj.skills.values()])
        
        prompt = f"""Generate a behavioral interview question targeting the {comp_obj.name} competency.

Specific skills to assess: {skills_list}

Difficulty level: {difficulty}
Intent: {intent}
Role: {self.competency_model.role}
Experience level: {self.competency_model.experience_level}

Requirements:
- Ask for a specific example or situation from their experience
- The question should naturally elicit evidence of the target skills
- Use STAR method framework (Situation, Task, Action, Result)
- Difficulty {difficulty} means {"asking about recent, straightforward scenarios" if difficulty == "easy" else "asking about complex, challenging scenarios" if difficulty == "hard" else "asking about typical professional scenarios"}

Generate ONE clear, focused question."""
        
        return prompt
    
    def get_follow_up_question(self, response_analysis: Dict, original_competency: str) -> Tuple[str, str, Dict]:
        missing_elements = response_analysis.get("missing_elements", [])
        depth_score = response_analysis.get("depth_score", 5)
        
        if "situation" in missing_elements or "context" in missing_elements:
            follow_up = "Can you provide more context about the situation? What were the specific circumstances?"
            intent = "clarify_context"
            
        elif "action" in missing_elements or "approach" in missing_elements:
            follow_up = "What specific steps did you take? Walk me through your approach in detail."
            intent = "clarify_action"
            
        elif "result" in missing_elements or "outcome" in missing_elements:
            follow_up = "What was the outcome? Can you quantify the impact or results?"
            intent = "clarify_outcome"
            
        elif depth_score < 4:
            follow_up = "Could you elaborate on that with more specific details or examples?"
            intent = "increase_depth"
            
        else:
            comp_obj = self.competency_model.competencies[original_competency]
            skills = list(comp_obj.skills.keys())
            follow_up = f"""That's helpful. To understand your {comp_obj.name} better, can you give me another example that demonstrates {skills[0].replace('_', ' ')}?"""
            intent = "explore_breadth"
        
        metadata = {
            "question_type": "follow_up",
            "target_competency": original_competency,
            "difficulty": "medium",
            "intent": intent,
            "based_on": response_analysis
        }
        
        return follow_up, original_competency, metadata
    
    def should_probe_deeper(self, response_analysis: Dict) -> bool:
        depth_score = response_analysis.get("depth_score", 5)
        specificity_score = response_analysis.get("specificity_score", 5)
        completeness_score = response_analysis.get("completeness_score", 5)
        
        avg_score = (depth_score + specificity_score + completeness_score) / 3
        
        return avg_score < 6.0