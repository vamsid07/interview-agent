import google.generativeai as genai
import time
import logging
from typing import Optional, Dict
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobustAPIClient:
    def __init__(self, api_key: str, model_name: str = 'gemini-2.0-flash-exp'):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.max_retries = 3
        self.base_delay = 1
        self.request_count = 0
        self.last_request_time = None
        
    def generate_content(self, prompt: str, context: str = "") -> Optional[str]:
        self._rate_limit_check()
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"API request attempt {attempt + 1}/{self.max_retries}")
                
                response = self.model.generate_content(prompt)
                
                if not response or not response.text:
                    logger.warning(f"Empty response on attempt {attempt + 1}")
                    if attempt < self.max_retries - 1:
                        self._exponential_backoff(attempt)
                        continue
                    return None
                
                self.request_count += 1
                self.last_request_time = datetime.now()
                
                logger.info(f"API request successful. Response length: {len(response.text)}")
                return response.text.strip()
                
            except Exception as e:
                error_type = type(e).__name__
                error_msg = str(e)
                
                logger.error(f"API error on attempt {attempt + 1}: {error_type} - {error_msg}")
                
                if self._is_rate_limit_error(e):
                    logger.warning("Rate limit hit, backing off significantly")
                    time.sleep(60)
                    continue
                
                if self._is_quota_error(e):
                    logger.error("API quota exceeded")
                    return None
                
                if self._is_network_error(e):
                    logger.warning(f"Network error, retrying in {self._get_backoff_delay(attempt)} seconds")
                    if attempt < self.max_retries - 1:
                        self._exponential_backoff(attempt)
                        continue
                
                if attempt == self.max_retries - 1:
                    logger.error(f"All retry attempts failed. Last error: {error_msg}")
                    return None
                
                self._exponential_backoff(attempt)
        
        return None
    
    def _rate_limit_check(self):
        if self.last_request_time:
            time_since_last = (datetime.now() - self.last_request_time).total_seconds()
            if time_since_last < 0.5:
                sleep_time = 0.5 - time_since_last
                logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
    
    def _exponential_backoff(self, attempt: int):
        delay = self.base_delay * (2 ** attempt)
        jitter = delay * 0.1
        total_delay = delay + jitter
        logger.info(f"Backing off for {total_delay:.2f} seconds")
        time.sleep(total_delay)
    
    def _get_backoff_delay(self, attempt: int) -> float:
        return self.base_delay * (2 ** attempt)
    
    def _is_rate_limit_error(self, error: Exception) -> bool:
        error_msg = str(error).lower()
        rate_limit_indicators = [
            'rate limit', 'too many requests', '429', 'quota',
            'resource exhausted', 'rate_limit_exceeded'
        ]
        return any(indicator in error_msg for indicator in rate_limit_indicators)
    
    def _is_quota_error(self, error: Exception) -> bool:
        error_msg = str(error).lower()
        quota_indicators = [
            'quota exceeded', 'insufficient quota', 'billing',
            'payment required', 'quota limit'
        ]
        return any(indicator in error_msg for indicator in quota_indicators)
    
    def _is_network_error(self, error: Exception) -> bool:
        error_types = [
            'ConnectionError', 'TimeoutError', 'Timeout',
            'ConnectionResetError', 'BrokenPipeError'
        ]
        return type(error).__name__ in error_types
    
    def get_stats(self) -> Dict:
        return {
            'total_requests': self.request_count,
            'last_request': self.last_request_time.isoformat() if self.last_request_time else None
        }