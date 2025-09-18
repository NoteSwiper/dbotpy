import logging
import logging.handlers

from typing import Mapping, Optional
from discord.ext import commands
import discord

import stuff

stuff.create_dir_if_not_exists("./logs")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(
    filename="logs/help_command.log",
    encoding='utf-8',
    maxBytes=32*1024*1024,
    backupCount=128,
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')

handler.setFormatter(formatter)
logger.addHandler(handler)

class MyHelpCommand(commands.HelpCommand):
    
    def __init__(self):
        super().__init__(
            show_hidden=False,
            command_attrs={"brief": "Shows help"}
        )
    
    async def send_bot_help(self, mapping: Mapping[Optional[commands.Cog], list[commands.Command]]):
        e = discord.Embed(
            title="Help",
            description="Lists of commands! :3"
        )
        
        for cog, cmds in mapping.items():
            temp1 = ""
            cog_name = cog.qualified_name if cog else "Uncategorized"
            for command in cmds:
                c_name = command.name
                c_desc = command.description or "No description provided"
                
                temp1 = temp1 + f"\n`{c_name}` - {c_desc}"
            e.add_field(
                name=f"Category: {cog_name} :3",
                value=temp1,
                inline=False,
            )
        
        channel = self.get_destination()
        
        if channel:
            await channel.send(embed=e)
            logger.info("Sent help command!")
        else:
            logger.error("Destination channel not found. ignoring help output...")
    
    async def send_cog_help(self, cog):
        embed = discord.Embed(
            title=f"{cog.qualified_name} Commands :3",
            description=cog.description or "No description provided 3:",
            color=discord.Color.green()
        )
        for command in cog.get_commands():
            embed.add_field(
                name=f"`{command.name}`",
                value=command.help or "No help text 3:",
                inline=False,
            )
        await self.get_destination().send(embed=embed)
    
    async def send_command_help(self, command):
        embed = discord.Embed(
            title=f"Help with `{command.name}` :3",
            description=command.help or "No help text 3:",
            color=discord.Color.red()
        )
        if command.aliases:
            embed.add_field(
                name="Aliases :3",
                value=", ".join(f"`{alias}`" for alias in command.aliases),
                inline=False
            )
        if command.usage:
            embed.add_field(
                name="Usage :3",
                value=f"`{command.usage}` :3",
                inline=False
            )
        await self.get_destination().send(embed=embed)