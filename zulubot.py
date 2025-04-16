import discord
import os
import asyncio
import threading
import signal
import sys
import speech_2_text.speech_2_text as s2t
import prompt_llm.prompt_llm as pllm
import text_2_speech.text_2_speech as t2s
from dotenv import load_dotenv
from discord.ext import commands
from discord import FFmpegPCMAudio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

stop_event = threading.Event()
exit_event = threading.Event()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.command()
async def zulusummon(ctx):
    global stop_event
    stop_event.clear()

    # check if summoner is in voice channel
    if not ctx.author.voice:
        await ctx.send("Yu ah not in de channel")
        return
    
    channel = ctx.author.voice.channel
    await channel.connect()
    await ctx.send(f"De Zulu is hia.")
    
    # check that the bot is in voice channel
    if ctx.voice_client:
        # source = discord.FFmpegPCMAudio('assets/zulu.m4a')
        # ctx.voice_client.play(source)

        def send_message(text):
            coro = ctx.send(f"De Zulu has herd yu. Yu sed:\n{text}")
            asyncio.run_coroutine_threadsafe(coro, bot.loop)        # allow async to run from normal thread

            try:
                print(f"Prompting de LLM: {text}")
                llm_reply = pllm.prompt_llm(text)
                
                # run async text-to-speech coroutine safely from thread
                future = asyncio.run_coroutine_threadsafe(t2s.text_2_speech(llm_reply), bot.loop)
                tts_path = future.result()

                if tts_path and ctx.voice_client:
                    source = FFmpegPCMAudio(tts_path)
                    ctx.voice_client.play(source)

                # wait until audio is done playing before deleting
                while ctx.voice_client.is_playing():
                    asyncio.run_coroutine_threadsafe(asyncio.sleep(1), bot.loop).result()

                os.remove(tts_path)
                
            except Exception as e:
                print(f"Error while sending LLM reply: {e}")
                coro = ctx.send("De Zulu has lost contact with de spirit realm.")
                asyncio.run_coroutine_threadsafe(coro, bot.loop)

        # run speech2text in background thread
        await asyncio.to_thread(s2t.transcribe, stop_event, send_message)

        # disconnect after finishing
        await ctx.voice_client.disconnect()
        await ctx.send("De Zulu is gon.")

@bot.command()
async def zulubegone(ctx):
    global stop_event
    stop_event.set()     # break the transcribe() loop if running to avoid hanging function

    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("De Zulu is gon.")
    else:
        await ctx.send("De Zulu is not in de channel")

 # handle termination signals like Ctrl+C
def signal_handler(sig, frame):
   
    print("\nGracefully shutting down...")
    
    # signal threads to stop
    stop_event.set()
    exit_event.set()
    
    # schedule bot to close
    asyncio.run_coroutine_threadsafe(bot.close(), bot.loop)
    
    print("Cleanup complete. Exiting.")
    sys.exit(0)

# register signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

bot.run(TOKEN)