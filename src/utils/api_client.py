import os
import time
import logging
import json
import re
import streamlit as st  
from typing import Optional, Dict, Any
from groq import Groq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobustAPIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model_name = "llama-3.3-70b-versatile" 
        self.is_mock = os.getenv("USE_MOCK_API", "False").lower() == "true"
        self.max_retries = 3
        
        if not self.is_mock:
            if not self.api_key:
                st.error("🚨 CRITICAL: GROQ_API_KEY is missing from environment variables.")
                st.stop()
                
            try:
                self.client = Groq(api_key=self.api_key)
                self.client.models.list() 
            except Exception as e:
                logger.error(f"Failed to init Groq client: {e}")
                st.error(f"🚨 ERROR CONNECTING TO GROQ API: {e}")
                st.info("Please check your internet connection and verify the API Key is correct.")
                st.stop()
        else:
            self.is_mock = True

    def generate_content(self, prompt: str) -> Optional[str]:
        if self.is_mock: return self._mock_text()

        for attempt in range(self.max_retries):
            try:
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.6,
                    max_tokens=1024,
                    top_p=1,
                    stop=None,
                    stream=False
                )
                return completion.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"API Attempt {attempt+1} failed: {e}")
                time.sleep(2)
        
        return None

    def generate_json_content(self, prompt: str) -> Optional[Dict[str, Any]]:
        if self.is_mock: return self._mock_json()

        for attempt in range(self.max_retries):
            try:
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that outputs ONLY valid JSON."},
                        {"role": "user", "content": f"{prompt}\n\nRespond ONLY with a JSON object."}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"} 
                )
                
                text = completion.choices[0].message.content.strip()
                return json.loads(text)
            except Exception as e:
                logger.error(f"JSON Attempt {attempt+1} failed: {e}")
                time.sleep(2)
                
        return None

    def _mock_text(self):
        time.sleep(0.5)
        return "Mock Mode Active. (If you see this, check USE_MOCK_API in .env)"

    def _mock_json(self):
        time.sleep(0.5)
        return {"strategy": "MOVE_ON", "reasoning": "Mock Mode", "detected_persona": "Neutral", "focus_areas": []}
