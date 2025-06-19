# modules/llm_client.py
import os
import random
import base64
import tempfile
import uuid
from PIL import Image
from google import genai
from io import BytesIO
from google.genai import types
from dotenv import load_dotenv
class LLMClient:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        self.client = genai.Client(api_key=api_key)
        self.text_model = "gemini-2.5-flash"
        self.image_model = "gemini-2.0-flash-preview-image-generation"
    
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
                model=self.text_model,
                contents=full_prompt,
                config=types.GenerateContentConfig(safety_settings=safety_settings),
            )
            return response.text
            
        except Exception as e:
            print(f"Error from LLM: {e}")
            return random.choice(error_messages)
        

    def generate_image(self, message, context, error_messages):
        """generate image from llm"""
        try:
            prompt = ('Please generate an image based on the following description: ')

            # combine context with message
            full_prompt = context + prompt + message

            response = self.client.models.generate_content(
                model= self.image_model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
                )
            )

            text_response = None
            image_path = None

            # parse response parts
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    text_response = part.text
                    print("Generated text:", part.text)
                elif part.inline_data is not None:
                    # create temp file with unique name
                    temp_dir = tempfile.gettempdir()
                    image_filename = f"zuludraw_image_{uuid.uuid4().hex}.png"
                    image_path = os.path.join(temp_dir, image_filename)
                    
                    # save image to temp file
                    image = Image.open(BytesIO(part.inline_data.data))
                    image.save(image_path)
                    print(f"image saved to: {image_path}")
                
            # return both text and image path
            if text_response and image_path:
                return (text_response, image_path)
            else:
                return random.choice(error_messages)

        except Exception as e:
            print(f"Error from LLM: {e}")
            return random.choice(error_messages)