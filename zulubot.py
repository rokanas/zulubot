import discord
import os
import asyncio
import threading
import speech_2_text.speech_2_text as s2t
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

stop_event = threading.Event()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.command()
async def zulusummon(ctx):
    global stop_event
    stop_event.clear()

    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"De Zulu is hia.")
        if ctx.voice_client:
            source = discord.FFmpegPCMAudio('assets/zulu.m4a')
            ctx.voice_client.play(source)

            # run speech2text in background thread
            await asyncio.to_thread(s2t.transcribe, stop_event)

            # read output file
            try:
                with open("speech_2_text/output.txt", "r") as f:
                    text = f.read().strip()
                    if text:
                        # discord max limit is 2000 characters
                        if len(text) <= 2000:
                            await ctx.send(f"De Zulu has herd yu. Yu sed:\n{text}")
                        else:
                            await ctx.send("Yu tok tu much. Characta limit is tu tousend")
                            await ctx.send(file=discord.File("output.txt"))
                    else:
                        await ctx.send("De Zulu herd nuttin.")
            except FileNotFoundError:
                await ctx.send("De Zulu found no output.")

            # disconnect after finishing
            if ctx.voice_client:
                await ctx.voice_client.disconnect()
                await ctx.send("De Zulu is gon.")

    else:
        await ctx.send("Yu ah not in de channel")

@bot.command()
async def zulubegone(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("De Zulu is gon.")
    else:
        await ctx.send("De Zulu is not in de channel")

bot.run(TOKEN)