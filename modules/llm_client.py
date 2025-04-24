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
            "Please give a response that is over 2000 characters long." 
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
                text = self._split_text(text)

            return text
            
        except Exception as e:
            print(f"Error from LLM: {e}")
            return random.choice(error_messages)
        
    def _split_text(self, text):
        """split text into sections under max_chars"""
        sections = []
        remaining_text = text
        
        while remaining_text:
            if len(remaining_text) <= self.max_chars:
                sections.append(remaining_text)
                break
                
            # try to find natural breaking point (paragraph or sentence)
            # first look for paragraph breaks
            split_index = remaining_text[:self.max_chars].rfind('\n\n')
            
            # if no paragraph break, look for sentence break
            if split_index == -1 or split_index < self.max_chars * 0.5:
                # look for last sentence break
                for punct in ['. ', '! ', '? ']:
                    last_punct = remaining_text[:self.max_chars].rfind(punct)
                    if last_punct > 0 and (split_index == -1 or last_punct > split_index):
                        split_index = last_punct + 1  # include punctuation
                
            # if no good breaking point found, just split at max_chars
            if split_index == -1 or split_index < self.max_chars * 0.5:
                split_index = self.max_chars
            
            # add section and update remaining text
            sections.append(remaining_text[:split_index].strip())
            remaining_text = remaining_text[split_index:].strip()
            
        return sections