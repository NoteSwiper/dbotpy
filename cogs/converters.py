import discord
from discord import app_commands
from discord.ext import commands
import requests

import stuff

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
            await ctx.reply(f"<@{ctx.author.id}>: {stuff.base64_decode(text)}")
        except Exception as e:
            await ctx.reply(f"Error: {e} 3:")
    
    @commands.hybrid_command(name="mmphify", description="muffles your response")
    @app_commands.describe(text="Message to be MMMPHHHH-ified")
    async def muffle(self, ctx: commands.Context, text: str):
        try:
            await ctx.reply(stuff.muffle(text))
        except Exception as e:
            await ctx.reply(f"Error: {e} 3:")
    

# i will add this but not this time :(
# https://colornames.org/search/json/?hex=FF0000

async def setup(bot):
    await bot.add_cog(Converters(bot))