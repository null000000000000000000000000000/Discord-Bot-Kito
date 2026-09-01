import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from sqlalchemy.future import select
from database.manager import get_session
from database.models import ModerationCase, Guild, User
from utils.helpers import create_embed, success_embed, error_embed, format_time
from utils.config import ERROR_COLOR, SUCCESS_COLOR, EMBED_COLOR
from utils.errors import PermissionError
from utils.permissions import has_permissions, bot_has_permissions

class ModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._spam_tracker: dict[int, list[float]] = {}

    async def _get_modlog_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        return discord.utils.get(guild.text_channels, name="mod-logs") or discord.utils.get(guild.text_channels, name="modlog")

    async def _send_modlog(self, guild: discord.Guild, embed: discord.Embed):
        channel = await self._get_modlog_channel(guild)
        if channel:
            try:
                await channel.send(embed=embed)
            except Exception:
                pass

    async def _create_case(self, guild_id: int, user_id: int, moderator_id: int, action: str, reason: str | None = None) -> ModerationCase:
        async with get_session() as session:
            case = ModerationCase(
                guild_id=guild_id,
                user_id=user_id,
                moderator_id=moderator_id,
                action=action,
                reason=reason or "No reason provided"
            )
            session.add(case)
            await session.commit()
            await session.refresh(case)
            return case

    @commands.hybrid_command(name="warn", description="Warn a user")
    @has_permissions(moderate_members=True)
    @bot_has_permissions(moderate_members=True)
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str | None = None):
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send(embed=error_embed("You cannot warn this user."))
            return
        case = await self._create_case(ctx.guild.id, member.id, ctx.author.id, "warn", reason)
        try:
            await member.send(f"You have been warned in **{ctx.guild.name}**\nReason: {reason or 'No reason provided'}\nCase ID: #{case.id}")
        except Exception:
            pass
        embed = create_embed(
            title="User Warned",
            color=EMBED_COLOR,
        )
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
        embed.set_footer(text=f"Case #{case.id}")
        await ctx.send(embed=embed)
        await self._send_modlog(ctx.guild, embed)

    @commands.hybrid_command(name="mute", description="Timeout a user")
    @has_permissions(moderate_members=True)
    @bot_has_permissions(moderate_members=True)
    async def mute(self, ctx: commands.Context, member: discord.Member, duration: str, *, reason: str | None = None):
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send(embed=error_embed("You cannot mute this user."))
            return
        units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        try:
            seconds = int(duration)
        except ValueError:
            seconds = 0
            for i in range(len(duration)):
                if duration[i].isdigit():
                    continue
                if duration[i] in units:
                    seconds += int(duration[:i]) * units[duration[i]]
                    break
            if seconds == 0:
                await ctx.send(embed=error_embed("Invalid duration format. Use e.g. 10m, 1h, 1d"))
                return
        if seconds > 28 * 24 * 60 * 60:
            await ctx.send(embed=error_embed("Maximum timeout duration is 28 days."))
            return
        case = await self._create_case(ctx.guild.id, member.id, ctx.author.id, "mute", reason)
        try:
            await member.timeout(discord.utils.utcnow() + timedelta(seconds=seconds), reason=reason)
        except Exception:
            await ctx.send(embed=error_embed("Failed to timeout user."))
            return
        embed = create_embed(
            title="User Muted",
            color=EMBED_COLOR,
        )
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Duration", value=format_time(seconds), inline=True)
        embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
        embed.set_footer(text=f"Case #{case.id}")
        await ctx.send(embed=embed)
        await self._send_modlog(ctx.guild, embed)

    @commands.hybrid_command(name="unmute", description="Remove timeout from a user")
    @has_permissions(moderate_members=True)
    @bot_has_permissions(moderate_members=True)
    async def unmute(self, ctx: commands.Context, member: discord.Member):
        await member.timeout(None)
        await ctx.send(embed=success_embed(f"Removed timeout from {member.mention}"))

    @commands.hybrid_command(name="kick", description="Kick a user from the server")
    @has_permissions(kick_members=True)
    @bot_has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str | None = None):
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send(embed=error_embed("You cannot kick this user."))
            return
        case = await self._create_case(ctx.guild.id, member.id, ctx.author.id, "kick", reason)
        try:
            await member.kick(reason=reason)
        except Exception:
            await ctx.send(embed=error_embed("Failed to kick user."))
            return
        embed = create_embed(title="User Kicked", color=EMBED_COLOR)
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
        embed.set_footer(text=f"Case #{case.id}")
        await ctx.send(embed=embed)
        await self._send_modlog(ctx.guild, embed)

    @commands.hybrid_command(name="ban", description="Ban a user from the server")
    @has_permissions(ban_members=True)
    @bot_has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str | None = None):
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send(embed=error_embed("You cannot ban this user."))
            return
        case = await self._create_case(ctx.guild.id, member.id, ctx.author.id, "ban", reason)
        try:
            await member.ban(reason=reason)
        except Exception:
            await ctx.send(embed=error_embed("Failed to ban user."))
            return
        embed = create_embed(title="User Banned", color=EMBED_COLOR)
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
        embed.set_footer(text=f"Case #{case.id}")
        await ctx.send(embed=embed)
        await self._send_modlog(ctx.guild, embed)

    @commands.hybrid_command(name="unban", description="Unban a user")
    @has_permissions(ban_members=True)
    @bot_has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user_id: str):
        try:
            user_id_int = int(user_id)
        except ValueError:
            await ctx.send(embed=error_embed("Invalid user ID."))
            return
        try:
            user = await self.bot.fetch_user(user_id_int)
            await ctx.guild.unban(user)
            await ctx.send(embed=success_embed(f"Unbanned {user.mention}"))
        except discord.NotFound:
            await ctx.send(embed=error_embed("User not found in ban list."))
        except Exception:
            await ctx.send(embed=error_embed("Failed to unban user."))

    @commands.hybrid_command(name="purge", description="Delete multiple messages")
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, limit: int):
        if limit < 1 or limit > 500:
            await ctx.send(embed=error_embed("Limit must be between 1 and 500."))
            return
        try:
            deleted = await ctx.channel.purge(limit=limit)
            await ctx.send(embed=success_embed(f"Deleted {len(deleted)} messages."), delete_after=5)
        except Exception:
            await ctx.send(embed=error_embed("Failed to delete messages."))

    @commands.hybrid_command(name="history", description="View moderation history for a user")
    @has_permissions(moderate_members=True)
    async def history(self, ctx: commands.Context, member: discord.Member | None = None):
        target = member or ctx.author
        async with get_session() as session:
            result = await session.execute(
                select(ModerationCase).where(
                    ModerationCase.guild_id == ctx.guild.id,
                    ModerationCase.user_id == target.id
                ).order_by(ModerationCase.created_at.desc()).limit(10)
            )
            cases = result.scalars().all()
        if not cases:
            await ctx.send(embed=create_embed(description=f"No moderation history for {target.mention}"))
            return
        embed = create_embed(title=f"Moderation History — {target}", color=EMBED_COLOR)
        for case in cases:
            embed.add_field(
                name=f"Case #{case.id} | {case.action.title()}",
                value=f"Moderator: <@{case.moderator_id}>\nReason: {case.reason}\nDate: {discord.utils.format_dt(case.created_at, 'R')}",
                inline=False
            )
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ModerationCog(bot))
