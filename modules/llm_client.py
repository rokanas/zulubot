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

            return response.text
            
        except Exception as e:
            print(f"Error from LLM: {e}")
            return random.choice(error_messages)