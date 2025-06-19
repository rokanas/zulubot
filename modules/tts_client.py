# modules/tts_client.py
import os
import uuid
import aiofiles
from elevenlabs.client import AsyncElevenLabs
from dotenv import load_dotenv
from pathlib import Path

class TTSClient:
    def __init__(self): # default zulu warrior voice id
        load_dotenv()
        api_key = os.getenv("ELEVENLABS_API_KEY")
        self.client = AsyncElevenLabs(api_key=api_key)
        
        # create download directory if nonexistent
        self.download_dir = "downloads"
        Path(self.download_dir).mkdir(exist_ok=True)
    
    async def generate_speech(self, text, voice_id):
        """generate speech from text and save to temporary file"""
        try:
            # elevenlabs sends back audio as stream of chunks
            stream = await self.client.generate(
                text=text,
                voice=voice_id,
                # model="eleven_multilingual_v2",
                stream=True
            )
            
            # give sound file random uuid filename in downloads folder
            file_name = f"output_{uuid.uuid4()}.mp3"
            file_path = os.path.join(self.download_dir, file_name)
            
            # asynchronously open file and write to it chunk by chunk
            async with aiofiles.open(file_path, "wb") as f:
                async for chunk in stream:
                    await f.write(chunk)
                    
            return file_path
            
        except Exception as e:
            print(f"Error generating TTS: {e}")
            return None