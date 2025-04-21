# zulubot.py - main bot file
import os
import asyncio
import threading
import signal
import sys
import random
from dotenv import load_dotenv
import discord
from discord.ext import commands

from modules.speech_processor import SpeechProcessor
from modules.llm_client import LLMClient
from modules.tts_client import TTSClient
from modules.crypto_client import CryptoClient

# unused error message: "De Zulu can track de great wildebeest, but (...)"

# load env variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class ZuluBot:
    def __init__(self):
        # initialize discord bot
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        intents.guilds = True
        
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self.setup_commands()
        
        # initialize clients
        self.llm = LLMClient()
        self.tts = TTSClient()
        self.crypto = CryptoClient()
        self.speech_processor = SpeechProcessor()
        
        # control flags
        self.stop_event = threading.Event()
        
        # setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)

        # error messages
        self.error_messages = [
            "De Zulu has lost contact with de spirit realm. Try agen soon",
            "De Zulu is lost in de savannah. Try agen soon.",
            "De Zulu lost de battle wit de lion. Try agen soon.",
            "De wisdom of de Zulu is clouded. Try agen soon.",
        ]
    
    def setup_commands(self):
        """setup zulubot !commands"""
        @self.bot.event
        async def on_ready():
            print(f'Logged in as {self.bot.user}!')
        
        @self.bot.command()
        async def zulusummon(ctx):
            await self.handle_summon(ctx)

        @self.bot.command()
        async def zuluask(ctx, *, text=""):
            await self.handle_ask(ctx, text)
            
        @self.bot.command()
        async def zulubegone(ctx):
            await self.handle_begone(ctx)

        @self.bot.command()
        async def zulucrypto(ctx, *, text=""):
            await self.handle_crypto(ctx, text)
        
    async def handle_summon(self, ctx):
        self.stop_event.clear()
        
        # check if summoner is in voice channel
        if not ctx.author.voice:
            await ctx.send("Yu ah not in de channel.")
            return
        
        summoner_channel = ctx.author.voice.channel

        # check if zulubot is already in voice channel
        if ctx.voice_client and ctx.voice_client.is_connected():
            # if already in summoner's channel, do nothing
            if ctx.voice_client.channel == summoner_channel:
                await ctx.send("De Zulu is already in de channel.")
                return
            # if in different voice channel, move to summoner's
            else:
                await ctx.voice_client.move_to(summoner_channel)
                await ctx.send(f"De Zulu has moved ova to **{summoner_channel.name}**.")
                return

        # zulubot joins summoner's voice channel
        await summoner_channel.connect()
        await ctx.send(f"De Zulu is hia.")
        
        # start speech processing if connected to voice
        if ctx.voice_client:
            # create callback to handle transcribed text
            async def message_callback(text):
                await ctx.send(f"De Zulu has herd yu. Yu sed:\n{text}")
                await self.process_text_input(ctx, text)
            
            # run speech recognition in background
            await asyncio.to_thread(
                self.speech_processor.transcribe, 
                self.stop_event,
                lambda text: asyncio.run_coroutine_threadsafe(message_callback(text), self.bot.loop)
            )
            
            # disconnect after finishing
            if ctx.voice_client:
                await ctx.voice_client.disconnect()
                await ctx.send("De Zulu is gon.")

    async def handle_ask(self, ctx, text):
        """process user message from discord text chat"""
        # if user provides no text
        if not text:
            await ctx.send("Speak tu me, warrior! Yu must provide de text.")
            return
        
        if ctx.voice_client and ctx.voice_client.is_connected():
            # if bot is in voice channel, respond in voice chat (llm and tts pipeline)
            await self.process_text_input(ctx, text)
        else:
            # if not in voice channel, respond in text chat (llm only)
            llm_response = await asyncio.to_thread(self.llm.generate_response, text, self.error_messages)
            await ctx.send(llm_response)
    
    async def handle_begone(self, ctx):
        self.stop_event.set()

        if ctx.voice_client:
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            await ctx.send("De Zulu is gon.")
            print("Zulu disconnected from voice channel.")
        else:
            await ctx.send("De Zulu is not in de channel")

    async def handle_crypto(self, ctx, text):
        """fetch crypto data from coinmarketcap"""
        async with ctx.typing():
            crypto_data = await asyncio.to_thread(self.crypto.fetch_crypto_data, text)
            await ctx.send(embed=crypto_data)

    async def process_text_input(self, ctx, text):
        """process text through llm and tts pipeline"""
        try:
            # get llm response
            llm_response = await asyncio.to_thread(self.llm.generate_response, text, self.error_messages)
            
            # convert llm response to speech
            if ctx.voice_client:
                tts_path = await self.tts.generate_speech(llm_response)
                
                # play speech in voice channel
                if tts_path:
                    source = discord.FFmpegPCMAudio(tts_path)
                    ctx.voice_client.play(source)
                    print("LLM response:", llm_response)

                    # always send text response
                    await ctx.send(f"De Zulu speaks: {llm_response}")
                    
                    # wait for speech to finish playing
                    while ctx.voice_client and ctx.voice_client.is_playing():
                        await asyncio.sleep(0.5)

                    print("Listening again for activation phrase: 'Zulubot'")
                    
                    # clean up audio file
                    os.remove(tts_path)
                
        except Exception as e:
            print(f"Error in processing pipeline: {e}")
            await ctx.send(random.choice(self.error_messages))
    
    # signal handler for graceful shutdown (ctrol+c)
    def signal_handler(self, sig, frame):
        print("\nGracefully shutting down...")
        self.stop_event.set()
        asyncio.run_coroutine_threadsafe(self.bot.close(), self.bot.loop)
        print("Cleanup complete. Exiting.")
        sys.exit(0)
    
    def run(self):
        self.bot.run(TOKEN)

# run bot if file is executed directly
if __name__ == "__main__":
    bot = ZuluBot()
    bot.run()