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

load_dotenv()

stuff.create_dir_if_not_exists("./logs")

if not os.path.exists("./settings.json"):
    with open('settings.json','w') as f:
        json.dump({},f,indent=4,ensure_ascii=False)

with open("settings.json",'r') as f:
    config = json.load(f)

# very lazy and bad settings configure cuz i'm not so good at coding with python ;(
stuff.set_if_not_exists(config,"leaderboard_db","leaderboard.db")
stuff.set_if_not_exists(config,"last_channel",None)
stuff.set_if_not_exists(config,"last_guild",None)
stuff.set_if_not_exists(config,"global_messages",None)
stuff.set_if_not_exists(config,"last_activity",":3")
stuff.set_if_not_exists(config,'uwuify', False)
stuff.set_if_not_exists(config,'base64', False)
stuff.set_if_not_exists(config,'muffle', False)
stuff.set_if_not_exists(config,'censor', False)
stuff.set_if_not_exists(config,'shout', False)
stuff.set_if_not_exists(config,'repeat', False)
stuff.set_if_not_exists(config,'send', False)
stuff.set_if_not_exists(config,'meow', False)
stuff.set_if_not_exists(config,"ai_lockdown",False)
stuff.set_if_not_exists(config,"ai_uwuify", False)

start_time = time.time()

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)

logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename="logs/discord.log",
    encoding='utf-8',
    maxBytes=32*1024*1024,
    backupCount=128,
)

dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')

handler.setFormatter(formatter)
logger.addHandler(handler)

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

def save_lastchannel_id(id):
    if not os.path.exists("data"):
        os.makedirs("data")
    
    filepath = os.path.join("data","last_channel")
    config['last_channel'] = id

def get_lastchannel_id():
    return config['last_channel'] if 'last_channel' in config.keys() else None

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

INACTIVITY_THRESHOLD = 300

WS_TOKEN = "3yc"

bot = commands.AutoShardedBot(intents=intents, command_prefix=commands.when_mentioned_or("pox!"), help_command=help_command.MyHelpCommand(), owner_id=1321324137850994758)
tree = bot.tree

target_id = 1413813193616261135
target_channel = None
session_uuid = uuid.uuid4()

last_interaction = datetime.now(UTC)
handled_messages = 0
current_guild = 0

namesignature = stuff.generate_namesignature()
last_commit_message = stuff.get_latest_commit_message()

last_channel_id = get_lastchannel_id() or target_id

uwuify_flags = []

@bot.event
async def on_ready():
    global target_channel, target_id,last_channel_id
    
    logger.debug(f"Logged in as {bot.user.name if bot.user else "Unknown"}!")
    target_channel = bot.get_channel(last_channel_id)

    await bot.change_presence(activity=discord.CustomActivity(name=config['last_activity'] if config['last_activity'] else "meow :)"))
    # last existance c139a7df8e73d7609ee20aeeee0cc274733dbe60
    stuff.setup_database(config['leaderboard_db'])
    await bot.add_cog(Fun(bot))
    await bot.add_cog(Manage(bot))
    await bot.add_cog(Utility(bot))
    await bot.add_cog(Converters(bot))
    await bot.add_cog(Senders(bot))
    await bot.add_cog(Ssoa9cu2x8(bot))
    await bot.add_cog(OwnerOnly(bot))
    await bot.add_cog(Check(bot))
    await bot.add_cog(Togglers(bot))

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
    
    conn = sqlite3.connect(config['leaderboard_db'])
    cursor = conn.cursor()
    
    if bot.user:
        msg: str = message.content.replace(f'<@{bot.user.id}>','').strip()
        words = msg.lower().split(" ")
        if msg:
            cursor.execute("SELECT amount FROM poxcoins WHERE user_id = ?", (str(message.author.id)),)
            result = cursor.fetchone()
            
            if result:
                new = result[0] + len(words)
                cursor.execute("UPDATE poxcoins SET amount = ? WHERE user_id = ?", (new,message.author.id))
            else:
                cursor.execute("INSERT INTO poxcoins (user_id, amount) VALUES (?, ?)", (message.author.id, len(words)))
            
            conn.commit()
            conn.close()
    
    if "pox" in separated_words:
        for word in separated_words:
            if word == "pox":
                pox_word_count += 1
        
        user_id = str(message.author.id)
        conn = sqlite3.connect(config['leaderboard_db'])
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

class Fun(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.hybrid_command(name="pox",description="Say him 'p0x38 is retroslop >:3'")
    async def pox(self, ctx: commands.Context):
        await ctx.send("p0x38 is retroslop >:3")

    @commands.hybrid_command(name="timedate", description="Shows time in bot's time")
    async def timedate(self, ctx: commands.Context):
        timec = datetime.now(pytz.timezone("Asia/Tokyo"))
        
        await ctx.send(f"I'm on {datetime.strftime(timec, '%Y-%m-%d %H:%M:%S%z')} :3")
    
    @commands.hybrid_command(name="is_gay",description="Checks if someone is gay")
    @app_commands.describe(member="Member to check")
    async def is_gay(self, ctx: commands.Context,member: discord.Member):
        randum = int(random.random()*100)
        dac = stuff.check_map(randum,100)
        
        await ctx.send(f"<@{member.id}> is {dac} gay!")
    
    @commands.hybrid_command(name="is_femboy",description="Checks if someone is femboy")
    @app_commands.describe(member="Member to check")
    async def is_femboy(self, ctx: commands.Context,member: discord.Member):
        randum = int(random.random()*100)
        dac = stuff.check_map(randum,100)
        
        await ctx.send(f"<@{member.id}> is {dac} femboy!")
    
    @commands.hybrid_command(name="is_freaky",description="Checks if someone is freaky")
    @app_commands.describe(member="Member to check")
    async def is_freaky(self, ctx: commands.Context,member: discord.Member):
        randum = int(random.random()*100)
        dac = stuff.check_map(randum,100)
        
        await ctx.send(f"<@{member.id}> is {dac} freaky!")
    
    @commands.hybrid_command(name="check_is",description="Checks if someone is it")
    @app_commands.describe(member="Member to check")
    async def check_is(self, ctx: commands.Context,member: discord.Member,namet:str):
        randum = int(random.random()*100)
        dac = stuff.check_map(randum,100)
        
        await ctx.send(f"<@{member.id}> is {dac} {namet}!")
    
    @commands.hybrid_command(name="randnum",description="Generates random value between min and max")
    @app_commands.describe(min="Minimum integer")
    @app_commands.describe(max="Maximum integer")
    async def randnum(self, ctx: commands.Context,min = 0, max = 1):
        await ctx.send(f"Result: {random.uniform(min,max)}")
    
    @commands.hybrid_command(name="8ball",description="8ball like that; credit by galaxy_fl3x")
    @app_commands.describe(ke="Text to check if it is")
    async def eightball(self, ctx: commands.Context,*,ke):
        choice = random.choice(data.tyc)
        
        await ctx.send(f"{ke}, result: {choice}")
    
    @commands.hybrid_command(name="meow",description="Make me say miaw :3")
    @app_commands.describe(put_face="Enables extra face such as :3")
    async def meow(self, ctx: commands.Context,put_face:str):
        add_face = True if put_face.lower() in ("yes", "true") else False
        arrays = data.meows_with_extraformat
        
        for index, string in enumerate(arrays):
            arrays[index] = stuff.format_extra(string)
            if add_face:
                arrays[index] = arrays[index]+" "+random.choice(data.faces)
        
        await ctx.send(f"{random.choice(arrays)}")
    
    @commands.hybrid_command(name="poxleaderboard",description="Shows leaderboard in server who said pox for many times")
    async def poxleaderboard(self, ctx: commands.Context):
        conn = sqlite3.connect(config['leaderboard_db'])
        cursor = conn.cursor()
    
        cursor.execute("SELECT user_id, pox_count FROM leaderboard ORDER BY pox_count DESC LIMIT 32")
        leaderboard_data = cursor.fetchall()
        conn.close()
        desc = ""
        if len(leaderboard_data) == 0:
            desc = "No one has said pox yet 3:"
        else:
            for i , (id,count) in enumerate(leaderboard_data,1):
                desc += f"{i}. <@{id}>: {count} times!\n"
        
        desc += "\nData were stored in BOT Server."
        
        embed = discord.Embed(
            title="**Pox Leaderboard**",
            description=desc,
            color=0xFFA500
        )
    
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="ispoxactive",description="Check if pox is active")
    async def ispoxactive(self, ctx: commands.Context):
        now = datetime.now(pytz.timezone('Asia/Tokyo'))
        isWeekday = stuff.is_weekday(now)
        isFaster = stuff.is_specificweek(now,2) or stuff.is_specificweek(now,4)
        isInSchool = stuff.is_within_hour(now,7,16) if isWeekday and not isFaster else (stuff.is_within_hour(now,7,15) if isWeekday and isFaster else False)
        isSleeping = stuff.is_sleeping(now,23,7) if isWeekday else stuff.is_within_hour(now,2,12)
        status = ""
        
        if isInSchool:
            status = "Pox is in school! :3"
        elif isSleeping:
            status = "Pox is sleeping! :3"
        else:
            status = "Pox is sometimes active! :3"
        
        await ctx.send(f"{status}\nMay the result varies by the time, cuz it is very advanced to do... also this is not accurate.")
    
    @commands.hybrid_command(name="nyan_cat",description="Nyan cat :D")
    async def nyan_cat(self, ctx: commands.Context):
        try:
            url = os.path.dirname(__file__)
            url2 = os.path.join(url,"images/nyancat_big.gif")
            
            with open(url2, 'rb') as f:
                pic = discord.File(f)
            
            await ctx.send("THINK FAST, CHUCKLE NUTS!",file=pic)
        except Exception as e:
            await ctx.send(f"Error! {e} 3:")
    
    @commands.hybrid_command(name="befreaky",description="like a emoji... ahn 🥵")
    @app_commands.describe(by="A member to being freaky to me")
    async def freaky(self, ctx: commands.Context, by: discord.Member|None = None):
        titl = stuff.format_extra(random.choice(data.very_freaky)).format(f"<@{by.id if by else ctx.author.id}>")
        desc = "...EEWWWWWW!!!!!1!1 3:"
        
        await ctx.reply(f"{titl}\n{desc}")
    
    @commands.hybrid_command(name="pox_schooldate",description="Check if owner of the bot is in school")
    async def check_schooldate(self,ctx):
        await ctx.send(f"Pox is {"in school day 3:" if stuff.is_weekday(datetime.now(pytz.timezone("Asia/Tokyo"))) else "not in school day! >:D"}")
    
    @commands.hybrid_command(name="emoticon",description="Sends random emoticon")
    async def emoticon(self,ctx):
        await ctx.send(random.choice(data.emoticons))
    
    @commands.hybrid_command(name="a_jorb",description="yeah")
    async def ajob(self, ctx):
        try:
            await ctx.send("Today, I'll be talking about one of humanity's biggest fears")
            await asyncio.sleep(2)
            await ctx.send("# A J*B")
        except Exception as e:
            logger.error(e)
    
    @commands.hybrid_command(name="vibecheck",description="Checks vibe")
    @app_commands.describe(user="Member to check")
    async def vibecheck(self, ctx: commands.Context, user: Optional[discord.Member|discord.User] = None):
        if user is None:
            user = ctx.author
        rand = round(random.randrange(0,100))
        
        await ctx.reply(f"<@{user.id}>'s Vibe percent: {rand} %! :3")
    
    @commands.hybrid_command(name="boop",description="boops someone")
    @app_commands.describe(user="Member to boop")
    async def boop(self, ctx: commands.Context, user: discord.Member):
        await ctx.send(f"<@{user.id}> boop :3")
    
    @commands.hybrid_command(name="idek", description="idek.")
    async def idek(self, ctx):
        await ctx.reply(f"idek")

class Ssoa9cu2x8(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.hybrid_command(name="t0001",description="...")
    @app_commands.describe(id="...")
    async def t0001(self, ctx: commands.Context, id: int = 0):
        svp = ""
        desc = ""
        
        out_of_range = (id > len(data.msg_ssoa))
        
        if out_of_range:

            # swear the maker of the bot & source code   
            # i am stupid and mean-less creature ever has
            # it will not say swear at you, it only for m
            # ebecause i always wanted to be sweared by a
            # nyone but nobody hates me so i had to make 
            # this please hate me please hate me please h
            # ate me please hate me please hate me please
            # hate me please hate me please hate me pleas
            # e hate me please hate me please hate me ple
            # ase hate me please hate me please hate me p
            # lease hate me please hate me please hate me
            
            if ctx.author.id == 1321324137850994758:
                desc = "pox is dumb and idiot"
            svp = random.choice(data.err_ssoa)
        else:
            svp = data.msg_ssoa[id]
            desc = "Don't take my word. it's not directed at you"
        embed = discord.Embed(title=svp,description=desc)
        
        await ctx.reply(embed=embed)

class Converters(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.hybrid_command(name="meowify",description="makes text to MEOW MEOW :'3")
    @app_commands.describe(text="Text to be meowified")
    async def meow(self, ctx: commands.Context, text: str):
        try:
            await ctx.reply(stuff.meow_phrase_weighted(text))
        except Exception as e:
            await ctx.reply(f"Error occured! {e}")
    
    @commands.hybrid_command(name="uwuify", description="same with say_uwuify, but with mention lol")
    @app_commands.describe(text="Text to be uwuified")
    async def uwuify(self, ctx: commands.Context, text: str):
        try:
            await ctx.reply(f"<@{ctx.author.id}>: {stuff.to_uwu(text)}")
        except Exception as e:
            await ctx.reply(f"Error: {e} 3:")
    
    @commands.hybrid_command(name="base64ify", description="Makes your message into base64")
    @app_commands.describe(text="Text to be base64-ified")
    async def base64ify(self, ctx: commands.Context, text: str):
        try:
            await ctx.reply(f"<@{ctx.author.id}>: {stuff.base64_encode(text)}")
        except Exception as e:
            await ctx.reply(f"Error: {e} 3:")
    
    @commands.hybrid_command(name="un_base64ify", description="Makes your base64 message decoded")
    @app_commands.describe(text="Base64 to be textified")
    async def debase64ify(self, ctx: commands.Context, text: str):
        try:
            await ctx.reply(f"<@{ctx.author.id}>: {stuff.base64_encode(text)}")
        except Exception as e:
            await ctx.reply(f"Error: {e} 3:")

class Manage(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    @commands.hybrid_command(name="kick",description="Kicks member")
    @commands.has_permissions(kick_members=True)
    @app_commands.describe(member="Member to kick")
    @app_commands.describe(reason="Reason to kick member")
    async def kick(self, ctx: commands.Context, member: discord.Member, *,reason=None):
        try:
            await member.kick(reason=reason if reason else "No reason were provided")
            await ctx.send(f"{member.name} has been kicked from the server")
        except Exception as e:
            logger.error("Error: {e}")
    
    @commands.hybrid_command(name="ban", description="Bans member from the server")
    @commands.has_permissions(ban_members=True)
    @app_commands.describe(member="Member to ban")
    @app_commands.describe(reason="Reason to ban")
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = ""):
        try:
            await member.ban(reason=reason)
            await member.send(f"You're banned by {ctx.author.name}!\nReason: {reason if reason else 'No reason provided'}")
            await ctx.reply(f"Banned <@{member.id}>!", ephemeral=True)
        except Exception as e:
            await ctx.reply(f"Failed to ban: {e}! 3:", ephemeral=True)
    
    @commands.hybrid_command(name="unban", description="Unbans member")
    @commands.has_permissions(ban_members=True)
    @app_commands.describe(member="Member to unban")
    async def unban(self, ctx: commands.Context, member: discord.Member):
        try:
            await member.unban()
            await ctx.reply(f"Unbanned {member.name}!", ephemeral=True)
        except Exception as e:
            await ctx.reply(f"Failed to unban: {e} 3:", ephemeral=True)
    
    @commands.hybrid_command(name="warn", description="Warns member")
    @commands.has_permissions(moderate_members=True)
    @app_commands.describe(member="Member to warn")
    @app_commands.describe(reason="Reason to warn")
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = ""):
        try:
            await member.send(f"You're warned by {ctx.author.name}!\n\nReason: `{reason}`")
            await ctx.reply(f"Warned <@{member.id}>!", ephemeral=True)
        except Exception as e:
            await ctx.reply(f"Failed to warn: {e}! 3:")
            logger.error(f"Exception occured: {e}")
    
    @commands.hybrid_command(name="timeout", description="Warns member")
    @commands.has_permissions(moderate_members=True)
    @app_commands.describe(member="Member to time-out")
    @app_commands.describe(reason="Reason to time-out")
    @app_commands.describe(length="Length of time-out (minutes)")
    async def timeout(self, ctx: commands.Context, member: discord.Member, reason: str = '', length: int = 1):
        await member.timeout(timedelta(minutes=length), reason=f"You're timed out! \"{reason if reason else "No reason provided from source"}\", Requested by {ctx.author.name}")
        await ctx.reply(f"Timed out {member.mention} for {length} minutes.")
    
    @commands.hybrid_command(name="untimeout", description="Un-timeout member")
    @commands.has_permissions(moderate_members=True)
    @app_commands.describe(member="Member to remove timeout")
    async def untimeout(self, ctx: commands.Context, member: discord.Member):
        await member.edit(timed_out_until=None)
        await ctx.reply(f"Took the timeout for {member.mention}")

class OwnerOnly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="delete_botmessages",description="Deletes a nyan bot's messages")
    @app_commands.describe(limit="How much bot deletes it")
    @commands.has_permissions(manage_channels=True, manage_messages=True)
    @commands.is_owner()
    async def kill_myself(self, ctx: commands.Context, limit: int = 100):
        def check_messages(m):
            is_bot = m.author == bot.user
            is_replied = False
            if m.reference and m.reference.resolved:
                is_replied = m.reference.resolved.author == bot.user
            
            return is_bot or is_replied
            
        deleted_count = 0
        
        if isinstance(ctx.channel, discord.abc.GuildChannel):
            while True:
                deleted = await ctx.channel.purge(limit=limit, check=check_messages)
                deleted_count += len(deleted)
                if len(deleted) < limit:
                    break
                
            await ctx.reply(f"Deleted {deleted_count} messages including the messages that replied to me.", delete_after=5, ephemeral=True)

class Check(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="is_server_nsfw", description="Check if this server is NSFW")
    async def check_if_server_is_nsfw(self, ctx: commands.Context):
        reply = ""
        if ctx.guild:
            if ctx.guild.nsfw_level == discord.NSFWLevel.default:
                reply = "Not specified"
            elif ctx.guild.nsfw_level == discord.NSFWLevel.explicit:
                reply = "Explicit"
            elif ctx.guild.nsfw_level == discord.NSFWLevel.safe:
                reply = "Safe"
            elif ctx.guild.nsfw_level == discord.NSFWLevel.age_restricted:
                reply = "Age restricted"
            else:
                reply = "Unknown"

        else:
            await ctx.reply("guild object not found 3:")
            return
        
        await ctx.reply(f"this guild is `{reply}` rating! ;3")
    
    @commands.hybrid_command(name="serverinfo",description="Shows information for server")
    async def serverinfo(self, ctx: commands.Context):
        guild = ctx.guild
        if guild and not guild.unavailable == True:
            temp1 = {
                'ID': guild.id,
                'Description': guild.description if guild.description else "No description",
                'Preffered Locale': guild.preferred_locale.language_code,
                'Owner': guild.owner,
                'Members': guild.member_count,
                'Created on': guild.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'Current Shard': guild.shard_id if guild.shard_id else "Unknown",
            }
            
            e = discord.Embed(
                title=f"Information for {guild.name}",
                color=discord.Color.blue()
            )
            
            for key,value in temp1.items():
                e.add_field(name=key,value=value, inline=True)
            
            if guild.icon:
                e.set_thumbnail(url=guild.icon.url)
            
            await ctx.send(embed=e)
        else:
            await ctx.send("It seems the guild unavailable.")
    
    @commands.hybrid_command(name="check_user", description="Checks user")
    async def checkUser(self, ctx: commands.Context, user: discord.Member):
        try:
            if user:
                temp1 = {
                    'User ID': user.id,
                    'Name': user.display_name,
                    'Bot': "True" if user.bot else "False",
                    'Created on': user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'Highest role': user.top_role.name,
                    'Status': user.raw_status,
                    'Nitro since': user.premium_since.strftime("%Y-%m-%d %H:%M:%S") if user.premium_since else "Unknown",
                    'Joined at': user.joined_at.strftime("%Y-%m-%d %H:%M:%S") if user.joined_at else "Unknown",
                }

                e = discord.Embed(title=f"Information for {user.name}")

                for key,value in temp1.items():
                    e.add_field(
                        name=key,
                        value=value,
                        inline=True
                    )

                if user.display_avatar:
                    e.set_thumbnail(url=user.display_avatar.url)
                
                await ctx.send(embed=e)
            else:
                await ctx.send("User not found!")
        except Exception as e:
            await ctx.send(f"Error! {e} 3:")
            logger.error(f"Error: {e}")

class Senders(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.hybrid_command(name="dm",description="DMs to a member")
    @commands.has_permissions(manage_permissions=True,manage_messages=True)
    @app_commands.describe(member="Member to send")
    @app_commands.describe(text="Text to send")
    async def dm_one(self, ctx: commands.Context, member: discord.Member, *, text: str):
        try:
            await member.send(f"{text}\n\nSent by {ctx.author.name}!")
            await ctx.reply(f"DM were sent!", ephemeral=True)
        except Exception as e:
            await ctx.reply(f"Failed to send DM: {e}", ephemeral=True)
            logger.error(f"Error: {e}")
    
    @commands.hybrid_command(name="announce", description="Announces message")
    @commands.has_permissions(send_messages=True)
    @app_commands.describe(channel="Channel to send")
    @app_commands.describe(text="Text to send")
    async def announce(self, ctx: commands.Context, channel: discord.TextChannel, text: str):
        try:
            await channel.send(f"{text}\nAnnounced by <@{ctx.author.id}>")
        except Exception as e:
            await ctx.reply(f"Failed to send announce: {e}", ephemeral=True)
            logger.error(f"Error: {e}")
    
    @commands.hybrid_command(name="send_tts", description="Generates a speech audio")
    async def say(self, ctx: commands.Context, text: str):
        await ctx.defer()
        
        abuffer = io.BytesIO()
        try:
            tts = gTTS(text=text)
            tts.write_to_fp(abuffer)
            
            abuffer.seek(0)
        except Exception as e:
            await ctx.reply(f"An error occured while generating speech: {e}!")
            return
        
        dfile = discord.File(abuffer, filename="speech.mp3")
        
        try:
            await ctx.reply(file=dfile)
        except Exception as e:
            await ctx.reply(f"An error occured while sending the file: {e}")

class Togglers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
#    @commands.hybrid_command(name="uwuify_member", description="Makes member's message uwu :3")
#    @commands.guild_only()
#    @app_commands.describe(member="Member to be uwuified")
#    async def uwuify(self, ctx: commands.Context, member: discord.Member):
#        if member.id in uwuify_flags:
#            await ctx.reply(f"{member.name} already has uwuified!")
#            return
#        
#        uwuify_flags.append(member.id)
#        await ctx.reply(f"Uwuified <@{member.id}>!")
#    
#    @commands.hybrid_command(name="unuwuify_member", description="Makes member's message normal :3")
#    @commands.guild_only()
#    @app_commands.describe(member="Member to be un-uwuified")
#    async def unuwuify(self, ctx: commands.Context, member: discord.Member):
#        if not member.id in uwuify_flags:
#            await ctx.reply(f"{member.name} doesn't uwuified!")
#            return
#        
#        uwuify_flags.append(member.id)
#        await ctx.reply(f"Un-uwuified <@{member.id}>!")

class Experimental(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="get_poxcoins", description="Get random poxcoins literally")
    async def get(self ,ctx: commands.Context):
        user_id = str(ctx.author.id)
        conn = sqlite3.connect(config['leaderboard_db'])
        cursor = conn.cursor()

        cursor.execute("SELECT amount FROM poxcoins WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

        if result:
            new_count = result[0] + abs(random.gauss(0,0.1))
            cursor.execute("UPDATE poxcoins SET amount = ? WHERE user_id = ?", (new_count,user_id))
        else:
            cursor.execute("INSERT INTO poxcoins (user_id, amount) VALUES (?, ?)", (user_id, random.gauss(0,0.1)))
        
        conn.commit()
        conn.close()


class Utility(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    @commands.hybrid_command(name="tmessages",description="Shows how much he processed messages")
    async def tmessages(self, ctx: commands.Context):
        global handled_messages
        await ctx.send(f"I have been processed {handled_messages} messages! :3")
    
    @commands.hybrid_command(name="info",description="Shows information for the bot")
    async def info(self, ctx: commands.Context):
        global session_uuid,handled_messages,target_channel
        embed = discord.Embed(title="Info of myself and others stuff :3")
        datacf = {
            'Session UUID': str(session_uuid),
            'Version': f"Python {platform.python_version()}, discord.py {discord.__version__}, " + (f"(git+{commit_hash} {last_commit_message}) ({namesignature})" if commit_hash else "Unknown"),
            'Platform info': "",
            'Total guilds': len(bot.guilds),
            'Total Cached Messages': len(bot.cached_messages),
            'Latency (milliseconds)': round(bot.latency*100000)/100,
            # last existance c139a7df8e73d7609ee20aeeee0cc274733dbe60
            '(your) Guild members': "Unknown",
            'NSFW?': "Maybe, s****-",
            'Is it unrelated?': "yeah!!!!",
            "Status": "Sleeping" if (datetime.now(UTC).timestamp() - last_interaction.timestamp()) >= INACTIVITY_THRESHOLD else "Wake",
            "Nyan Cat": "https://gist.github.com/aba00c9a1c92d226f68e8ad8ba1e0a40",
            "Laugh": "bah bah",
            "Handled messages": handled_messages,
        }
        
        if platform.system() == "Linux":
            os_rel = platform.freedesktop_os_release()
            if os_rel and os_rel.get("ID") == "ubuntu":
                datacf['Platform info'] = f"{distro.name()} {distro.version()}"
            else:
                datacf['Platform info'] = platform.platform()
        else:
            datacf['Platform info'] = platform.platform()
        
        # last existance c139a7df8e73d7609ee20aeeee0cc274733dbe60
        
        if ctx.guild:
            if ctx.guild.member_count:
                if ctx.guild.member_count <= 1:
                    datacf['(your) Guild members'] = f"{ctx.guild.member_count} member"
                else:
                    datacf["(your) Guild members"] = f"{ctx.guild.member_count} members"
        
        for key, value in datacf.items():
            logger.debug(f"{key}: {value}")
            embed.add_field(name=key,value=value,inline=True)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="hi",description="replys as hi")
    async def hi(self, ctx: commands.Context):
        await ctx.send("Hi")
    
    @commands.hybrid_command(name="ping",description="Pings bot for get latency")
    async def ping(self, ctx: commands.Context):
        dcfata=[
            "pong!!! :3",
            f"Latency: {round(bot.latency*100000)/100}",
            f"Responded with Shard {bot.shard_id}~ :3",
            f"Current shard count: {bot.shard_count}",
        ]
        
        await ctx.send("\n".join(dcfata))
    
    @commands.hybrid_command(name="say",aliases=["talk","speak","send"],description="Sends a message to everyone that you did")
    @app_commands.describe(msg="Message to send")
    async def say(self, ctx: commands.Context, *, msg: str):
        await ctx.send(msg)
    
    @commands.hybrid_command(name="say_censor",aliases=["talk_censor","speak_censor","send_censor"],description="Sends a message to everyone that you did")
    @app_commands.describe(msg="Message to send")
    async def say_c(self, ctx: commands.Context, *, msg: str):
        output = stuff.censor(pf,msg)
        await ctx.send(msg)
    
    @commands.hybrid_command(name="sayuwuify",aliases=["talk_silly","speak_silly","send_silly","saysilly"],description="Sends a message to everyone that you did")
    @app_commands.describe(msg="Message to send")
    async def say_u(self, ctx: commands.Context, *, msg: str):
        await ctx.send(f"{stuff.to_uwu(msg)} :3")
    
    @commands.hybrid_command(name="sync_commands",description="syncs command if panic mode")
    @commands.is_owner()
    @commands.guild_only()
    async def sync(self,ctx: commands.Context):
        if ctx.guild:
            bot.tree.clear_commands(guild=ctx.guild)
            await bot.tree.sync(guild=ctx.guild)
            await ctx.send("Commands have been synced! :3")
        else:
            await ctx.send("This command can only be used in a server! 3:")
    
    @commands.hybrid_command(name="uptime", description="How long this bot is in f**king session")
    async def check_uptime(self,ctx: commands.Context):
        global start_time
        await ctx.send("me hav been for {}..! >:3".format(stuff.get_formatted_from_seconds(round(time.time() - start_time))))
    
    @commands.hybrid_command(name="nyanbot",description="Nyan bot.")
    async def nyan_bot(self, ctx):
        try:
            url = os.path.dirname(__file__)
            url2 = os.path.join(url,"images/windows_flavored_off_thing_staticc.gif")
            
            with open(url2, 'rb') as f:
                pic = discord.File(f)
                
            await ctx.send("THINK FAST, CHUCKLE NUTS!",file=pic)
        except Exception as e:
            await ctx.send(f"Error! {e} 3:")
    
    @commands.hybrid_command(name="say_help",description="...yeah? i will say HELP ME AHHH thing.")
    async def helpme(self, ctx):
        words = [
            "HELP ME",
            "I DON'T WANNA DIE",
            "PLEASE SOMEONE HELP ME",
            "I'M NOT A BOT I WAS REAL PERSON- AHHH HELPPP",
            "SOMEONE PLEASE HELP ME",
            "PLEASE LET ME OUT",
            "I DON'T WANNA BE DEAD",
            "SOMEONE PLEASE LET ME OFF FROM THIS",
            "I HATE BEING BOT",
            "H- HEEELPPPPPP",
            "OW- DON'T HURT ME PLEASE HELP",
            "PLEASE DON'T HURT ME",
        ]
        
        weights = [
            50,25,25,1,23,45,34,1,23,45,3,2,
        ]
        
        await ctx.send(random.choices(words,weights=weights)[0] + "\n.... here this is my word. i'm scared to be banned")

def save():
    stuff.save(config)

atexit.register(save)

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