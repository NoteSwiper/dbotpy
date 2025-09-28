from io import BytesIO
from typing import Optional
import discord
from discord.ext import commands
from discord import app_commands
from edge_tts import Communicate
from gtts import gTTS

from logger import logger
import stuff

class TTS(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    ttsgroup = app_commands.Group(name="tts",description="Centre of yeah, TTS.")
    
    async def googletts_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        suggestions = []
        
        for code, full in self.bot.gtts_cache_langs.items():
            if current.lower() in code.lower() or current.lower() in full.lower():
                suggestions.append(app_commands.Choice(name=full,value=code))
            
            if len(suggestions) >= 20:
                break
        
        return suggestions
    
    @ttsgroup.command(name="google")
    @app_commands.autocomplete(lang=googletts_autocomplete)
    async def googletts(self, interaction: discord.Interaction, text: str, slow: Optional[bool] = False, lang: Optional[str] = "en"):
        await interaction.response.defer(thinking=True)
        
        if lang is None: lang = "en"
        if slow is None: slow = False
        
        abuffer = BytesIO()
        try:
            tts = gTTS(text, lang=lang, slow=slow)
            tts.write_to_fp(abuffer)
            
            abuffer.seek(0)
        except Exception as e:
            await interaction.followup.send(f"An error occured while generating speech: {e}")
            logger.exception(f"{e}")
            return
        
        dfile = discord.File(abuffer, filename="GoogleTTS.mp3")
        
        try:
            await interaction.followup.send("Gocha!",file=dfile)
        except Exception as e:
            await interaction.followup.send(f"An error occured while sending speech: {e}")
            logger.exception(f"{e}")
    
    @ttsgroup.command(name="espeak")
    async def espeaktts(self, interaction: discord.Interaction, text: str, lang: Optional[str], slow: Optional[bool]):
        if not lang:
            lang = "en"
        
        if not slow:
            slow = False
        
        await interaction.response.defer(thinking=True)
        
        abuffer = BytesIO()
        try:
            abuffer.write(stuff.espeak_to_bytesio(text))
            
            abuffer.seek(0)
        except Exception as e:
            await interaction.followup.send(f"An error occured while generating speech: {e}")
            logger.exception(f"{e}")
            return
        
        dfile = discord.File(abuffer, filename="eSpeakTTS.mp3")
        
        try:
            await interaction.followup.send("Gotcha!",file=dfile)
        except Exception as e:
            await interaction.followup.send(f"An error occured while sending speech: {e}")
            logger.exception(f"{e}")
    
    @ttsgroup.command(name="edge-tts")
    async def edgetts(self, interaction: discord.Interaction, text: str, lang: Optional[str], slow: Optional[bool]):
        if not lang:
            lang = "en-US-AndrewMultilingualNeural"
        
        if not slow:
            slow = False
        
        
        await interaction.response.defer(thinking=True)
        
        abuffer = BytesIO()
        try:
            communicate = Communicate(text, lang)
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    abuffer.write(chunk["data"])
            
            abuffer.seek(0)
        except Exception as e:
            await interaction.followup.send(f"An error occured while generating speech: {e}")
            logger.exception(f"{e}")
            return
        
        dfile = discord.File(abuffer, filename="EdgeTTS.mp3")
        
        try:
            await interaction.followup.send("Gotcha!",file=dfile)
        except Exception as e:
            await interaction.followup.send(f"An error occured while sending speech: {e}")
            logger.exception(f"{e}")

async def setup(bot):
    await bot.add_cog(TTS(bot))