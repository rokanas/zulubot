import os
from elevenlabs.client import AsyncElevenLabs
from dotenv import load_dotenv
import uuid
import aiofiles

load_dotenv()
API_KEY = os.getenv("ELEVENLABS_API_KEY")

eleven_client = AsyncElevenLabs(api_key=API_KEY)

async def text_2_speech(text):
    try:
        stream = await eleven_client.generate(
            text=text,
            voice="ddDFRErfhdc2asyySOG5",
            stream=True
        )

        file_name = f"output_{uuid.uuid4()}.mp3"

        async with aiofiles.open(file_name, "wb") as f:
            async for chunk in stream:
                await f.write(chunk)

        return file_name
    
    except Exception as e:
        print(f"Error generating TTS: {e}")
        return None