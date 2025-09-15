import discord
from discord.ext import commands

class MyHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Bot helps :3", description="Here's my commands :3", color=discord.Color.blue())
        for cog, cmds in mapping.items():
            if cmds:
                name = cog.qualified_name if cog else "No cat :3"
                command_list = [f"`{command.name}`" for command in cmds]
                embed.add_field(
                    name=name,
                    value=", ".join(command_list),
                    inline=False
                )
        await self.get_destination().send(embed=embed)
    
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