# zulubot.py - main bot file
import os
import re
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
from modules.yt_client import YTClient
from modules.audio_player import AudioPlayer

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
        self.yt_client = YTClient()
        self.audio_player = AudioPlayer()
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
        async def zulusummon(ctx, suppress_messages=False):
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

        @self.bot.command()
        async def zuluplay(ctx, *, text=""):
            await self.handle_play(ctx, text)

        @self.bot.command()
        async def zulupause(ctx):
            await self.handle_pause(ctx)

        @self.bot.command()
        async def zuluresume(ctx):
            await self.handle_resume(ctx)

        @self.bot.command()
        async def zuluskip(ctx):
            await self.handle_skip(ctx)

        @self.bot.command()
        async def zuluqueue(ctx):
            await self.handle_queue(ctx)

        @self.bot.command()
        async def zulustop(ctx):
            await self.handle_stop(ctx)

        @self.bot.command()
        async def zuluhelp(ctx):
            await self.handle_help(ctx)
        
    async def handle_summon(self, ctx, suppress_messages=False):
        """connect bot to voice channel"""
        self.stop_event.clear()

        # check if summoner is in voice channel
        if not ctx.author.voice:
            await ctx.send("Yu ah not in de channel.")
            return False
        
        summoner_channel = ctx.author.voice.channel

        #check if zulubot is already in voice channel
        if ctx.voice_client and ctx.voice_client.is_connected():
            # if already in summoner's channel, do nothing
            if ctx.voice_client.channel == summoner_channel:
                if not suppress_messages:
                    await ctx.send("De Zulu is already in de channel.")
                return True
            # if in different voice channel, move to summoner's
            else:
                try:
                    await ctx.voice_client.move_to(summoner_channel)
                    await ctx.send(f"De Zulu has moved ova to **{summoner_channel.name}**.")
                    asyncio.create_task(self.connect_voice(ctx))
                    return
                except Exception as e:
                    print(f"Error moving to voice channel: {e}")
                    await ctx.send("De Zulu cannot move to de channel. De path is blocked by lions.")
                    return False
            
        try:
            # zulubot joins summoner's voice channel
            await summoner_channel.connect()
            await ctx.send(f"De Zulu is hia.")
            asyncio.create_task(self.connect_voice(ctx))
            return True
        except Exception as e:
            print(f"Error connecting to voice channel: {e}")
            await ctx.send("De Zulu cannot connect to de channel. De path is blocked by lions.")
            return False

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
            if not text:
                # if user doesn't specify coin, get top coins
                crypto_data = await asyncio.to_thread(self.crypto.fetch_top_coins)
            else:
                # get user specified coin
                crypto_data = await asyncio.to_thread(self.crypto.fetch_coin_data, text)
            
            await ctx.send(embed=crypto_data)

    async def handle_play(self, ctx, text):
        """play music from youtube"""
        if not text:
            await ctx.send("Yu must provide mo info. Use **!zuluhelp** for de documentation.")
            return
        
        # connect to voice channel with suppressed messages
        await self.handle_summon(ctx, suppress_messages=True)

        # let user know we're processing
        processing_msg = await ctx.send("De Zulu is searching for de track...")

        if self.is_url(text):
            stream_url, title = await asyncio.to_thread(self.yt_client.get_audio_stream, text)
        else:
            stream_url, title = await asyncio.to_thread(self.yt_client.search_for_url, text)

        # if stream url not found
        if not stream_url:
            await processing_msg.edit(content="De Zulu cannot find dis track. It is probably age-restricted and yu ah but a beby. Zulu will fix anodda time")
            return
        
        # play stream and get resulting message
        message = await self.audio_player.play(ctx, stream_url, title, True)

        # update message
        await processing_msg.edit(content=message)

    async def handle_pause(self, ctx):
        """pause current playback"""
        message = await self.audio_player.pause(ctx.voice_client)
        await ctx.send(message)

    async def handle_resume(self, ctx): 
        """resume current playback"""
        message = await self.audio_player.resume(ctx.voice_client)
        await ctx.send(message)

    async def handle_skip(self, ctx): 
        """skip current playback in queue"""
        message = await self.audio_player.skip(ctx.voice_client)
        await ctx.send(message)

    async def handle_queue(self, ctx): 
        """display current queue"""
        message = await self.audio_player.get_queue()
        await ctx.send(message)

    async def handle_stop(self, ctx):
        """stop current playback"""
        message = await self.audio_player.stop(ctx.voice_client)
        await ctx.send(message)

    async def handle_help(self, ctx):
        """display list of commands"""
        commands_list = (
            "De Zulu is hia to help yu, *mlungu*! Use de following commands:\n\n"
            "**!zulusummon** - Connect to de voice channel\n"
            "**!zuluask *<text>* ** - Chat with de Zulu\n"
            "**!zulubegone** - Disconnect de Zulu from de voice channel\n"
            "**!zulucrypto** - Get de crypto data for de top coins\n"
            "**!zulucrypto *<coin_name>* ** - Get de crypto data for de specified coin\n"
            "**!zuluplay *<youtube_url* || *search_query>* ** - Play de music from youtube \n"
            "**!zulupause** - Pause de current playback\n"
            "**!zuluresume** - Resume de current playback\n"
            "**!zuluskip** - Skip current de playback and play de next in queue\n"
            "**!zuluqueue** - Display de current queue\n"
            "**!zulustop** - Stop de current playback and clear de queue\n"
            "**!zuluhelp** - Display dis help message\n"
        )
        await ctx.send(commands_list)
        
    async def connect_voice(self, ctx):
        """connect to voice channel and start speech recognition"""
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

    # consider moving to utils folder
    def is_url(self, text):
        """check if input is url and return boolean"""
        url_pattern = re.compile(
            r'^(https?:\/\/)?'          # optional http or https
            r'(www\.)?'                 # optional www
            r'([a-zA-Z0-9\-]+\.)+'      # domain name
            r'[a-zA-Z]{2,}'             # domain suffix
            r'(\/\S*)?$'                # optional trailing path
        )
        return bool(url_pattern.match(text))
    
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