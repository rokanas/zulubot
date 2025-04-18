# modules/tts_client.py
import os
import uuid
import aiofiles
from elevenlabs.client import AsyncElevenLabs
from dotenv import load_dotenv

class TTSClient:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("ELEVENLABS_API_KEY")
        self.client = AsyncElevenLabs(api_key=api_key)
        self.voice_id = "ddDFRErfhdc2asyySOG5"  # zulu warrior voice id
    
    async def generate_speech(self, text):
        """generate speech from text and save to temporary file"""
        try:
            # elevenlabs sends back audio as stream of chunks
            stream = await self.client.generate(
                text=text,
                voice=self.voice_id,
                stream=True
            )
            
            # give sound file random uuid filename
            file_name = f"output_{uuid.uuid4()}.mp3"
            
            # asynchronously open file and write to it chunk by chunk
            async with aiofiles.open(file_name, "wb") as f:
                async for chunk in stream:
                    await f.write(chunk)
                    
            return file_name
            
        except Exception as e:
            print(f"Error generating TTS: {e}")
            return None