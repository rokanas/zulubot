# modules/llm_client.py
import os
import random
from google import genai
from google.genai import types
from dotenv import load_dotenv

class LLMClient:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash"
    
    def generate_response(self, message, context, error_messages):
        """generate response from llm using zulu warrior persona"""
        try:
            # combine context with message
            full_prompt = context + message

            # config to disable safety settings         
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_NONE,
                ),
            ]
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config=types.GenerateContentConfig(safety_settings=safety_settings),
            )
            return response.text
            
        except Exception as e:
            print(f"Error from LLM: {e}")
            return random.choice(error_messages)