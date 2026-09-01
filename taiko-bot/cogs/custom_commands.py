import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
from sqlalchemy.future import select
from database.manager import get_session
from database.models import CustomCommand
from utils.helpers import create_embed, success_embed, error_embed
from utils.config import EMBED_COLOR, ERROR_COLOR
from utils.permissions import has_permissions

class CustomCommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._prefix_commands: dict[str, CustomCommand] = {}

    async def _load_guild_commands(self, guild_id: int):
        async with get_session() as session:
            result = await session.execute(select(CustomCommand).where(CustomCommand.guild_id == guild_id))
            commands = result.scalars().all()
        for cmd in commands:
            self._prefix_commands[cmd.name.lower()] = cmd

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self._load_guild_commands(guild.id)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await self._load_guild_commands(guild.id)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        prefix = commands.when_mentioned_or("!")(self.bot, message)
        if isinstance(prefix, str):
            prefixes = [prefix]
        else:
            prefixes = prefix
        for prefix in prefixes:
            if message.content.startswith(prefix):
                cmd_name = message.content[len(prefix):].split()[0].lower()
                cmd = self._prefix_commands.get(cmd_name)
                if cmd:
                    response = cmd.response.replace("{user}", message.author.mention).replace("{server}", message.guild.name)
                    await message.channel.send(response)
                    return

    @commands.hybrid_command(name="cccreate", description="Create a custom command")
    @has_permissions(manage_guild=True)
    async def create_cc(self, ctx: commands.Context, name: str, *, response: str):
        name = name.lower().replace(" ", "")
        if len(name) < 1 or len(name) > 50:
            await ctx.send(embed=error_embed("Command name must be 1-50 characters."))
            return
        async with get_session() as session:
            existing = await session.execute(select(CustomCommand).where(CustomCommand.guild_id == ctx.guild.id, CustomCommand.name == name))
            if existing.scalar_one_or_none():
                await ctx.send(embed=error_embed("A custom command with that name already exists."))
                return
            cc = CustomCommand(guild_id=ctx.guild.id, name=name, response=response, author_id=ctx.author.id)
            session.add(cc)
            await session.commit()
            await session.refresh(cc)
        self._prefix_commands[name] = cc
        await ctx.send(embed=success_embed(f"Custom command `{name}` created!"))

    @commands.hybrid_command(name="ccdelete", description="Delete a custom command")
    @has_permissions(manage_guild=True)
    async def delete_cc(self, ctx: commands.Context, name: str):
        name = name.lower()
        async with get_session() as session:
            result = await session.execute(select(CustomCommand).where(CustomCommand.guild_id == ctx.guild.id, CustomCommand.name == name))
            cc = result.scalar_one_or_none()
            if not cc:
                await ctx.send(embed=error_embed("Custom command not found."))
                return
            await session.delete(cc)
            await session.commit()
        self._prefix_commands.pop(name, None)
        await ctx.send(embed=success_embed(f"Custom command `{name}` deleted."))

    @commands.hybrid_command(name="cclist", description="List all custom commands")
    async def list_cc(self, ctx: commands.Context):
        async with get_session() as session:
            result = await session.execute(select(CustomCommand).where(CustomCommand.guild_id == ctx.guild.id))
            commands = result.scalars().all()
        if not commands:
            await ctx.send(embed=create_embed(description="No custom commands."))
            return
        embed = create_embed(title="Custom Commands", color=EMBED_COLOR)
        for cc in commands:
            embed.add_field(name=cc.name, value=cc.response[:100], inline=False)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(CustomCommandsCog(bot))
