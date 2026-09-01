import discord
from discord.ext import commands
from utils.helpers import create_embed, success_embed, error_embed
from utils.config import EMBED_COLOR
from utils.permissions import has_permissions

class WelcomeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._config: dict[int, dict] = {}

    def _get_config(self, guild_id: int) -> dict:
        if guild_id not in self._config:
            self._config[guild_id] = {
                "welcome_channel": None,
                "goodbye_channel": None,
                "auto_role": None,
                "welcome_message": "Welcome {user} to {server}!",
                "goodbye_message": "Goodbye {user}, we hope to see you again!",
            }
        return self._config[guild_id]

    @commands.hybrid_command(name="setwelcome", description="Set the welcome channel")
    @has_permissions(administrator=True)
    async def set_welcome(self, ctx: commands.Context, channel: discord.TextChannel | None = None):
        config = self._get_config(ctx.guild.id)
        config["welcome_channel"] = channel.id if channel else None
        await ctx.send(embed=success_embed(f"Welcome channel set to {channel.mention}" if channel else "Welcome channel cleared."))

    @commands.hybrid_command(name="setgoodbye", description="Set the goodbye channel")
    @has_permissions(administrator=True)
    async def set_goodbye(self, ctx: commands.Context, channel: discord.TextChannel | None = None):
        config = self._get_config(ctx.guild.id)
        config["goodbye_channel"] = channel.id if channel else None
        await ctx.send(embed=success_embed(f"Goodbye channel set to {channel.mention}" if channel else "Goodbye channel cleared."))

    @commands.hybrid_command(name="setautorole", description="Set the auto-role for new members")
    @has_permissions(administrator=True)
    async def set_auto_role(self, ctx: commands.Context, role: discord.Role | None = None):
        config = self._get_config(ctx.guild.id)
        config["auto_role"] = role.id if role else None
        await ctx.send(embed=success_embed(f"Auto-role set to {role.mention}" if role else "Auto-role cleared."))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        config = self._get_config(member.guild.id)
        if config["auto_role"]:
            role = member.guild.get_role(config["auto_role"])
            if role:
                try:
                    await member.add_roles(role, reason="Auto-role")
                except Exception:
                    pass
        if config["welcome_channel"]:
            channel = member.guild.get_channel(config["welcome_channel"])
            if channel:
                embed = create_embed(
                    title="Welcome!",
                    description=config["welcome_message"].replace("{user}", member.mention).replace("{server}", member.guild.name),
                    color=EMBED_COLOR
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                try:
                    await channel.send(embed=embed)
                except Exception:
                    pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        config = self._get_config(member.guild.id)
        if config["goodbye_channel"]:
            channel = member.guild.get_channel(config["goodbye_channel"])
            if channel:
                embed = create_embed(
                    title="Goodbye!",
                    description=config["goodbye_message"].replace("{user}", str(member)).replace("{server}", member.guild.name),
                    color=EMBED_COLOR
                )
                try:
                    await channel.send(embed=embed)
                except Exception:
                    pass

async def setup(bot: commands.Bot):
    await bot.add_cog(WelcomeCog(bot))
