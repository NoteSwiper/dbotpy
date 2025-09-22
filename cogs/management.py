from datetime import UTC, datetime, timedelta
from enum import Enum
import time
import io
import os
import platform
import random
from typing import Optional
import discord
from discord.ext import commands
from discord import app_commands
import distro
from gtts import gTTS
import data
from logger import logger
import stuff

from main import handled_messages, INACTIVITY_THRESHOLD, session_uuid, commit_hash, last_commit_message, last_interaction, namesignature, start_time

class SpeakEngineType(Enum):
    GOOGLE = 0
    ESPEAK = 1

class Management(commands.Cog):
    def __init__(self, bot):
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
    
    @commands.hybrid_command(name="delete_botmessages",description="Deletes a nyan bot's messages")
    @app_commands.describe(limit="How much bot deletes it")
    @commands.has_permissions(manage_channels=True, manage_messages=True)
    @commands.is_owner()
    async def kill_myself(self, ctx: commands.Context, limit: int = 100):
        await ctx.defer()
        
        def check_messages(m):
            is_bot = m.author == self.bot.user
            is_replied = False
            if m.reference and m.reference.resolved:
                is_replied = m.reference.resolved.author == self.bot.user
            
            return is_bot or is_replied
            
        deleted_count = 0
        
        if isinstance(ctx.channel, discord.abc.GuildChannel):
            while True:
                deleted = await ctx.channel.purge(limit=limit, check=check_messages)
                deleted_count += len(deleted)
                if len(deleted) < limit:
                    break
                
            await ctx.reply(f"Deleted {deleted_count} messages including the messages that replied to me.", delete_after=5, ephemeral=True)
            
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
                    'Highest role': f"<@{user.top_role.name}>",
                    'Status': user.raw_status,
                    'Nitro since': user.premium_since.strftime("%Y-%m-%d %H:%M:%S") if user.premium_since else "Unknown",
                    'Joined at': user.joined_at.strftime("%Y-%m-%d %H:%M:%S") if user.joined_at else "Unknown",
                    'Roles': [f"<@{role.id}>" for role in user.roles]
                }

                e = discord.Embed(title=f"Information for <@{user.id}>")

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
    
    @commands.hybrid_command(name="check_role", description="Checks role")
    async def checkRole(self, ctx: commands.Context, role: discord.Role):
        try:
            if role:
                temp1 = {
                    'Role ID': role.id,
                    'Role Name': role.name,
                    'Role Color': role.color,
                    'Created on': role.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'Managed Role?': "Yeah" if role.managed == True else ("Nah" if role.managed == False else "I dunno"),
                    "Can be mentioned": "Yup but don't spam it please" if role.mentionable == True else ("Nope" if role.mentionable == False else "I dunno"),
                    "It shown in member list?": "Ye" if role.hoist == True else ("Nuh uh" if role.hoist == False else "I dunno"),
                    "Position": role.position or "IDK",
                }

                e = discord.Embed(title=f"Information for <@{role.id}>")

                for key,value in temp1.items():
                    e.add_field(
                        name=key,
                        value=value,
                        inline=True
                    )

                if role.display_icon and isinstance(role.display_icon, discord.Asset):
                    e.set_thumbnail(url=role.display_icon.url)
                
                await ctx.send(embed=e)
            else:
                await ctx.send("User not found!")
        except Exception as e:
            await ctx.send(f"Error! {e} 3:")
            logger.error(f"Error: {e}")

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
    
    async def talkengine_autocomplete(self, ctx: discord.Interaction, current: str):
        choices = [
            app_commands.Choice(name=key, value=id)
            for key, id in data.VoiceEngineType.items() if current.lower() in key.lower()
        ]
        return choices[:3]
    
    @commands.hybrid_command(name="send_tts", description="Generates a speech audio")
    async def talk(self, ctx: commands.Context, text: str, engine: Optional[app_commands.Choice[str]], lang: str = "en"):
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

    @commands.hybrid_command(name="info",description="Shows information for the bot")
    async def info(self, ctx: commands.Context):
        global session_uuid,handled_messages,target_channel
        embed = discord.Embed(title="Info of myself and others stuff :3")
        datacf = {
            'Session UUID': str(session_uuid),
            'Version': f"Python {platform.python_version()}, discord.py {discord.__version__}, " + (f"(git+{commit_hash} {last_commit_message}) ({namesignature})" if commit_hash else "Unknown"),
            'Platform info': "",
            'Total guilds': len(self.bot.guilds),
            'Total Cached Messages': len(self.bot.cached_messages),
            'Latency (milliseconds)': round(self.bot.latency*100000)/100,
            # last existance c139a7df8e73d7609ee20aeeee0cc274733dbe60
            '(your) Guild members': "Unknown",
            'NSFW?': "Maybe, s****-",
            'Is it unrelated?': "yeah!!!!",
            "Status": "Sleeping" if (datetime.now(UTC).timestamp() - last_interaction.timestamp()) >= INACTIVITY_THRESHOLD else "Wake",
            "Nyan Cat": "https://gist.github.com/aba00c9a1c92d226f68e8ad8ba1e0a40",
            "Laugh": "bah bah",
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
    
    @commands.hybrid_command(name="latest_commit_data", description="Shows latest commit message and hash for this")
    async def get_commitdata(self, ctx: commands.Context):
        temp1 = {
            'Commit Hash': commit_hash,
            'Commit Message': last_commit_message,
        }
        
        e = discord.Embed(title="Current git information", url="https://github.com/NoteSwiper/dbotpy")
        
        for item, value in temp1.items():
            e.add_field(name=item,value=value)
        
        e.set_footer(text="The bot is open-source. Click to this embed to access the site which is published :3")
        
        await ctx.reply(embed=e)
    
    @commands.hybrid_command(name="hi",description="replys as hi")
    async def hi(self, ctx: commands.Context):
        await ctx.send("Hi")
    
    @commands.hybrid_command(name="ping",description="Pings bot for get latency")
    async def ping(self, ctx: commands.Context):
        dcfata=[
            "pong!!! :3",
            f"Latency: {round(self.bot.latency*100000)/100}",
            f"Responded with Shard {self.bot.shard_id}~ :3",
            f"Current shard count: {self.bot.shard_count}",
        ]
        
        await ctx.send("\n".join(dcfata))
    
    @commands.hybrid_command(name="say",aliases=["talk","speak","send"],description="Sends a message to everyone that you did")
    @app_commands.describe(msg="Message to send")
    async def say(self, ctx: commands.Context, *, msg: str):
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
            self.bot.tree.clear_commands(guild=ctx.guild)
            await self.bot.tree.sync(guild=ctx.guild)
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

async def setup(bot):
    await bot.add_cog(Management(bot))