# modules/llm_client.py
import os
import random
from google import genai
from dotenv import load_dotenv

class LLMClient:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash"
        self.context = (
            "Please limit your responses to 2000 characters." 
            "You are a mighty Zulu warrior. Answer the following message sounding like a mighty tribesman of the Zulu nation:\n\n"
        )
        self.max_chars = 2000
    
    def generate_response(self, message, error_messages):
        """generate response from llm using zulu warrior persona"""
        try:
            # combine context with message
            full_prompt = self.context + message
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )

            # get response text
            text = response.text

            # check if response exceeds character limit
            if len(text) > self.max_chars:
                text = self._shorten_text(text)

            return text
            
        except Exception as e:
            print(f"Error from LLM: {e}")
            return random.choice(error_messages)
        
    def _shorten_text(self, text):
        """shorten llm respose text (discord char limit)"""
        # if text is short enough, return as is
        if len(text) <= self.max_chars:
            return text
            
        # truncate and add ellipsis
        shortened = text[:self.max_chars-3] + "..."
        
        # find last complete sentence if possible
        last_period = shortened.rfind('.')
        if last_period > self.max_chars * 0.75:  # only use if not too much content is lost
            shortened = shortened[:last_period+1]
            
        return shortened