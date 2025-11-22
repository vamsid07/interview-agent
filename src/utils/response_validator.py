import re
from typing import Dict, Tuple

class ResponseValidator:
    def __init__(self):
        self.profanity_list = {
            'fuck', 'shit', 'damn', 'bitch', 'ass', 'bastard', 'crap',
            'piss', 'dick', 'cock', 'pussy', 'slut', 'whore', 'fag'
        }
        
        self.max_response_length = 2000
        self.min_response_length = 10
        
    def validate_user_response(self, response: str) -> Tuple[bool, str]:
        if not response or not response.strip():
            return False, "Response cannot be empty"
        
        if len(response) < self.min_response_length:
            return False, "Response is too short. Please provide more detail."
        
        if len(response) > self.max_response_length:
            return False, "Response is too long. Please keep it under 2000 characters."
        
        if self._contains_profanity(response):
            return False, "Please keep your response professional and appropriate."
        
        if self._is_gibberish(response):
            return False, "Response appears invalid. Please provide a meaningful answer."
        
        if self._is_potentially_copied(response):
            return False, "Please provide your own original response rather than copied content."
        
        return True, ""
    
    def validate_llm_question(self, question: str) -> Tuple[bool, str]:
        if not question or not question.strip():
            return False, "Generated question is empty"
        
        question_lower = question.lower()
        
        refusal_patterns = [
            "i cannot", "i can't", "i'm unable", "i apologize",
            "as an ai", "i don't have", "i'm not able",
            "it would be inappropriate", "i shouldn't"
        ]
        
        if any(pattern in question_lower for pattern in refusal_patterns):
            return False, "LLM refused to generate question"
        
        if not self._contains_question_marker(question):
            return False, "Generated text is not a question"
        
        if len(question.split()) < 5:
            return False, "Generated question is too short"
        
        if len(question) > 500:
            return False, "Generated question is too long"
        
        if self._is_generic_error(question):
            return False, "LLM generated error message"
        
        return True, ""
    
    def _contains_profanity(self, text: str) -> bool:
        words = re.findall(r'\b\w+\b', text.lower())
        return any(word in self.profanity_list for word in words)
    
    def _is_gibberish(self, text: str) -> bool:
        words = text.split()
        
        if len(words) < 3:
            return False
        
        non_alpha_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text)
        if non_alpha_ratio > 0.3:
            return True
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        if avg_word_length > 15 or avg_word_length < 2:
            return True
        
        unique_words = len(set(words))
        if unique_words < len(words) * 0.3:
            return True
        
        return False
    
    def _is_potentially_copied(self, text: str) -> bool:
        copied_indicators = [
            "according to", "source:", "reference:", "cited from",
            "as stated in", "from the article", "the document says"
        ]
        
        if any(indicator in text.lower() for indicator in copied_indicators):
            return True
        
        sentences = text.split('.')
        if len(sentences) > 5:
            very_long_sentences = sum(1 for s in sentences if len(s.split()) > 40)
            if very_long_sentences > len(sentences) * 0.5:
                return True
        
        return False
    
    def _contains_question_marker(self, text: str) -> bool:
        if '?' in text:
            return True
        
        question_starters = [
            'tell me', 'describe', 'explain', 'how do you', 'what would',
            'can you', 'could you', 'walk me through', 'give me an example',
            'share', 'discuss', 'elaborate'
        ]
        
        text_lower = text.lower()
        return any(text_lower.startswith(starter) or f' {starter}' in text_lower 
                   for starter in question_starters)
    
    def _is_generic_error(self, text: str) -> bool:
        error_patterns = [
            "error", "failed", "exception", "timeout", "rate limit",
            "quota exceeded", "service unavailable"
        ]
        
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in error_patterns)
    
    def sanitize_response(self, response: str) -> str:
        response = response.strip()
        
        response = re.sub(r'\s+', ' ', response)
        
        response = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', response)
        
        if len(response) > self.max_response_length:
            response = response[:self.max_response_length] + "..."
        
        return response