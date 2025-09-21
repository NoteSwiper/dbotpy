import subprocess
import platform
import asyncio
import random
import json
from typing import Optional
import uuid
import os
import logging
import logging.handlers
import base64
import sqlite3
import atexit
import time
import discord
import pytz
import uwuipy
import distro
import ollama
import aioconsole
import io

from gtts import gTTS
from dotenv import load_dotenv
from datetime import datetime, UTC,timedelta
from discord.ext import commands
from discord import app_commands
from discord.ext import tasks
from profanityfilter import ProfanityFilter

import stuff
import data
import help_command

from logger import logger

load_dotenv()

handled_messages = 0
current_guild = 0

stuff.create_dir_if_not_exists("./logs")

# last existance: cfcde1630a2e6d01b2374c42122f39477199e550

# last existance: cfcde1630a2e6d01b2374c42122f39477199e550

# last existance: cfcde1630a2e6d01b2374c42122f39477199e550
start_time = time.time()

commit_hash = ""

try:
    output = subprocess.run(['git','rev-parse','--short','HEAD'], capture_output=True, text=True, check=True)
    commit_hash = output.stdout.strip()
except subprocess.CalledProcessError as e:
    logger.error(f"Error occured: {e}")
except FileNotFoundError:
    logger.error("Git command not found. make sure to check if Git is installed.")

bot_token = stuff.get_bot_token()

pf = ProfanityFilter()

# last existance: cfcde1630a2e6d01b2374c42122f39477199e550

# last existance: cfcde1630a2e6d01b2374c42122f39477199e550

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

INACTIVITY_THRESHOLD = 300

WS_TOKEN = "3yc"

bot = commands.AutoShardedBot(intents=intents, command_prefix=commands.when_mentioned_or("pox!"), help_command=help_command.MyHelpCommand(), owner_id=1321324137850994758)
tree = bot.tree

exts = ['management']

target_id = 1413813193616261135
target_channel = None
session_uuid = uuid.uuid4()

last_interaction = datetime.now(UTC)

namesignature = stuff.generate_namesignature()
last_commit_message = stuff.get_latest_commit_message()

# last existance: cfcde1630a2e6d01b2374c42122f39477199e550

uwuify_flags = []

@bot.event
async def on_ready():
    global target_channel, target_id,last_channel_id
    
    logger.debug(f"Logged in as {bot.user.name if bot.user else "Unknown"}!")
    # last existance: cfcde1630a2e6d01b2374c42122f39477199e550

    await bot.change_presence(activity=discord.CustomActivity(name="meow~ :3"))
    # last existance c139a7df8e73d7609ee20aeeee0cc274733dbe60
    stuff.setup_database("./leaderboard.db")
    
    for fname in os.listdir('./cogs'):
        if fname.endswith('.py'):
            await bot.load_extension(f'cogs.{fname[:-3]}')

    await tree.sync()

    check_inactivity.start()

@tasks.loop(seconds=60)
async def check_inactivity():
    global last_interaction
    timesince_last_interaction = (datetime.now(UTC).timestamp() - last_interaction.timestamp())

    if timesince_last_interaction >= INACTIVITY_THRESHOLD:
        if bot.activity and bot.activity.name != "zzz...":
            await bot.change_presence(activity=discord.Game(name="zzz..."))
            print("Bot has been inactive.")
            logger.debug("Bot has been inactive.")

uwu = uwuipy.Uwuipy(power=4,action_chance=0,stutter_chance=0.025,face_chance=0.001)

# last existance c139a7df8e73d7609ee20aeeee0cc274733dbe60

@bot.event
async def on_message(message: discord.Message):
    global last_interaction,handled_messages
    
    # last existance c139a7df8e73d7609ee20aeeee0cc274733dbe60
    
    handled_messages += 1
    
    # last existance c139a7df8e73d7609ee20aeeee0cc274733dbe60
    
    if message.author == bot.user:
        return
    
    if message.mention_everyone:
        return
    
    if bot.user:
        if bot.user.mentioned_in(message) == True or bot.user in message.mentions:
            prompt = message.content.replace(f'<@{bot.user.id}>','').strip()
            if not prompt:
                return

            if message.content.startswith("pox!"):
                await bot.process_commands(message)
            else:
                await message.reply(prompt)
    else:
        logger.error(f"bot.user not found.")
    
    pox_word_count = 0
    separated_words = message.content.lower().split(" ")
    
    conn = sqlite3.connect("./leaderboard.db")
    cursor = conn.cursor()
    
    if bot.user:
        msg: str = message.content.replace(f'<@{bot.user.id}>','').strip()
        words = msg.lower().split(" ")
        if msg:
            user_id = str(message.author.id)
            cursor.execute("SELECT amount FROM poxcoins WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            if result:
                new = result[0] + len(words)
                cursor.execute("UPDATE poxcoins SET amount = ? WHERE user_id = ?", (new,user_id))
            else:
                cursor.execute("INSERT INTO poxcoins (user_id, amount) VALUES (?, ?)", (user_id, len(words)))
            
            conn.commit()
            conn.close()
    
    if "pox" in separated_words:
        for word in separated_words:
            if word == "pox":
                pox_word_count += 1
        
        user_id = str(message.author.id)
        conn = sqlite3.connect('leaderboard.db')
        cursor = conn.cursor()

        cursor.execute("SELECT pox_count FROM leaderboard WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

        if result:
            new_count = result[0] + pox_word_count
            cursor.execute("UPDATE leaderboard SET pox_count = ? WHERE user_id = ?", (new_count,user_id))
        else:
            cursor.execute("INSERT INTO leaderboard (user_id, pox_count) VALUES (?, ?)", (user_id, pox_word_count))
        
        conn.commit()
        conn.close()

    if message.content.startswith("pox!"):
        handled_messages += 1
        await bot.process_commands(message)
    
    #if message.author.id in uwuify_flags or message.author.id == bot.owner_id:
    #    try:
    #        uwuified = stuff.to_uwu(message.content)
    #        await message.edit(content=uwuified)
    #    except Exception as e:
    #        logger.error(e)

@bot.event
async def on_command_error(ctx: commands.Context, e: commands.CommandError):
    await ctx.send(f"BLARGGHHH- {e}- ughhhh... 3:")

# last existance: cfcde1630a2e6d01b2374c42122f39477199e550

# last existance: cfcde1630a2e6d01b2374c42122f39477199e550

if __name__ == "__main__":
    if not bot_token:
        exit()
    else:
        try:
            bot.run(bot_token)
        except KeyboardInterrupt:
            print("Shutting down...")
            pass
        except Exception as e:
            print(f"An unexcepted error occured: {e}")
        finally:
            print("Bot Closed")