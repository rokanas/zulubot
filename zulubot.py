import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.command()
async def zulujoin(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"De Zulu is hia.")
        if ctx.voice_client:
            source = discord.FFmpegPCMAudio('zulu.m4a')
            ctx.voice_client.play(source)

    else:
        await ctx.send("Yu ah not in de channel")

@bot.command()
async def zululeave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("De Zulu is gon.")
    else:
        await ctx.send("De Zulu is not in de channel")

bot.run(TOKEN)