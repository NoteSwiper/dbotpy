import asyncio
from io import BytesIO
import random
from typing import Optional
import os
import sqlite3
import discord
import markovify
from matplotlib import pyplot as plt
import profanityfilter
import pytz
from dotenv import load_dotenv
from datetime import datetime, UTC
from discord.ext import commands
from discord import app_commands

from others import censor
import stuff
import data

from logger import logger

class Silly(commands.Cog):
    def __init__(self, bot):
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
        conn = sqlite3.connect("leaderboard.db")
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
    
    @commands.hybrid_command(name="markov_test", description="don't use this cuz including NSFW words like c-")
    async def markv(self, ctx: commands.Context):
        with open("./others/markov.txt") as f:
            text = f.read()
        
        model = markovify.Text(text, state_size=3)
        
        result = model.make_sentence()
        
        pf = profanityfilter.ProfanityFilter()
        
        result = pf.censor(result)
        
        result = censor.censor(result)
        
        await ctx.reply(result)
    
    @commands.hybrid_command(name="targetclose", description="Target Closing Algorithm")
    async def targetclose(self, ctx: commands.Context, target_value: Optional[float]):
        histories = [stuff.approach_target(target_value or 20) for _ in range(10)]
        
        plt.figure(figsize=(12,8))
        for i, his in enumerate(histories):
            plt.plot(his, label=f"Attempt {i+1}")
        
        plt.axhline(y=target_value or 20, color='r', linestyle='--', label="Target")
        plt.title(f"Target close algorithm on {datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}")
        plt.xlabel("Steps")
        plt.ylabel("Value")
        plt.legend(loc='lower right')
        plt.grid(True)
        
        buffer = BytesIO()
        
        plt.savefig(buffer, format='png')
        
        buffer.seek(0)
        
        plt.close()
        
        file = discord.File(fp=buffer, filename='output.png')
        
        e = discord.Embed(title="Results with 'Target Close Algorithm'")
        for i,hist in enumerate(histories):
            e.add_field(name=f"Attempt #{i+1}",value=f"Length: {len(hist)}, Vx: \"{max(hist)},{min(hist)},{sum(hist)/len(hist)}\"")
        e.set_image(url="attachment://output.png")
        if file and e:
            await ctx.reply(file=file, embed=e)
        
        
async def setup(bot):
    await bot.add_cog(Silly(bot))