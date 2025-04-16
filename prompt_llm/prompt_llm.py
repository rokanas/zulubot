from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')

# create gemini client
client = genai.Client(api_key=API_KEY)

# take message and returns gemini's response
def prompt_llm(message: str) -> str:
    try:
        prefix = (
            "You are a mighty Zulu warrior. Answer the following message sounding like a mighty tribesman of the Zulu nation.:\n\n"
        )

        # combine prefix with the actual message
        full_prompt = prefix + message

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt
        )
        return response.text
    
    except Exception as e:
        print(f"Error from Gemini: {e}")
        return "De wisdom of de zulu is clouded right now. Try agen soon."