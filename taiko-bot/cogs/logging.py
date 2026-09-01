import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import create_embed, error_embed
from utils.config import ERROR_COLOR, EMBED_COLOR

class LoggingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._log_channels: dict[int, int] = {}

    def _get_log_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        channel_id = self._log_channels.get(guild.id)
        if channel_id:
            channel = guild.get_channel(channel_id)
            if channel:
                return channel
        return discord.utils.get(guild.text_channels, name="logs") or discord.utils.get(guild.text_channels, name="audit-log")

    async def _send_log(self, guild: discord.Guild, embed: discord.Embed):
        channel = self._get_log_channel(guild)
        if channel:
            try:
                await channel.send(embed=embed)
            except Exception:
                pass

    @commands.hybrid_command(name="setlogchannel", description="Set the logging channel")
    @has_permissions(administrator=True)
    async def set_log_channel(self, ctx: commands.Context, channel: discord.TextChannel | None = None):
        if channel:
            self._log_channels[ctx.guild.id] = channel.id
            await ctx.send(embed=success_embed(f"Log channel set to {channel.mention}"))
        else:
            self._log_channels.pop(ctx.guild.id, None)
            await ctx.send(embed=success_embed("Log channel cleared."))

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return
        embed = create_embed(title="Message Deleted", color=ERROR_COLOR)
        embed.add_field(name="Author", value=message.author.mention, inline=True)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        embed.add_field(name="Content", value=message.content or "*No text content*", inline=False)
        embed.set_footer(text=f"Message ID: {message.id}")
        await self._send_log(message.guild, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or before.content == after.content:
            return
        embed = create_embed(title="Message Edited", color=EMBED_COLOR)
        embed.add_field(name="Author", value=before.author.mention, inline=True)
        embed.add_field(name="Channel", value=before.channel.mention, inline=True)
        embed.add_field(name="Before", value=before.content or "*No text content*", inline=False)
        embed.add_field(name="After", value=after.content or "*No text content*", inline=False)
        embed.set_footer(text=f"Message ID: {before.id}")
        await self._send_log(before.guild, embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        embed = create_embed(title="Member Joined", color=0x57F287)
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="ID", value=str(member.id), inline=True)
        embed.add_field(name="Account Created", value=discord.utils.format_dt(member.created_at, style='R'), inline=False)
        await self._send_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        embed = create_embed(title="Member Left", color=ERROR_COLOR)
        embed.add_field(name="User", value=str(member), inline=True)
        embed.add_field(name="ID", value=str(member.id), inline=True)
        await self._send_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        changes = []
        if before.nick != after.nick:
            changes.append(f"Nickname: {before.nick} → {after.nick}")
        if before.roles != after.roles:
            added = [r.mention for r in after.roles if r not in before.roles]
            removed = [r.mention for r in before.roles if r not in after.roles]
            if added:
                changes.append(f"Roles added: {', '.join(added)}")
            if removed:
                changes.append(f"Roles removed: {', '.join(removed)}")
        if before.timed_out_until != after.timed_out_until:
            if after.timed_out_until:
                changes.append(f"Timed out until {discord.utils.format_dt(after.timed_out_until, style='R')}")
            else:
                changes.append("Timeout removed")
        if changes:
            embed = create_embed(title="Member Updated", color=EMBED_COLOR)
            embed.add_field(name="User", value=after.mention, inline=True)
            embed.add_field(name="Changes", value="\n".join(changes), inline=False)
            await self._send_log(after.guild, embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: abc.GuildChannel):
        embed = create_embed(title="Channel Created", color=0x57F287)
        embed.add_field(name="Name", value=channel.name, inline=True)
        embed.add_field(name="Type", value=str(channel.type), inline=True)
        await self._send_log(channel.guild, embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: abc.GuildChannel):
        embed = create_embed(title="Channel Deleted", color=ERROR_COLOR)
        embed.add_field(name="Name", value=channel.name, inline=True)
        embed.add_field(name="Type", value=str(channel.type), inline=True)
        await self._send_log(channel.guild, embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        embed = create_embed(title="Role Created", color=0x57F287)
        embed.add_field(name="Name", value=role.mention, inline=True)
        embed.add_field(name="Permissions", value=str(role.permissions.value), inline=True)
        await self._send_log(role.guild, embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        embed = create_embed(title="Role Deleted", color=ERROR_COLOR)
        embed.add_field(name="Name", value=role.name, inline=True)
        await self._send_log(role.guild, embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        changes = []
        if before.name != after.name:
            changes.append(f"Name: {before.name} → {after.name}")
        if before.permissions.value != after.permissions.value:
            changes.append("Permissions changed")
        if before.color != after.color:
            changes.append(f"Color changed")
        if changes:
            embed = create_embed(title="Role Updated", color=EMBED_COLOR)
            embed.add_field(name="Role", value=after.mention, inline=True)
            embed.add_field(name="Changes", value="\n".join(changes), inline=False)
            await self._send_log(after.guild, embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if before.channel == after.channel:
            return
        embed = create_embed(title="Voice State Update", color=EMBED_COLOR)
        embed.add_field(name="User", value=member.mention, inline=True)
        if before.channel and not after.channel:
            embed.add_field(name="Action", value=f"Left {before.channel.name}", inline=True)
        elif not before.channel and after.channel:
            embed.add_field(name="Action", value=f"Joined {after.channel.name}", inline=True)
        else:
            embed.add_field(name="From", value=before.channel.name, inline=True)
            embed.add_field(name="To", value=after.channel.name, inline=True)
        await self._send_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_ban(self, guild: discord.Guild, user: discord.User):
        embed = create_embed(title="User Banned", color=ERROR_COLOR)
        embed.add_field(name="User", value=str(user), inline=True)
        embed.add_field(name="ID", value=str(user.id), inline=True)
        await self._send_log(guild, embed)

    @commands.Cog.listener()
    async def on_unban(self, guild: discord.Guild, user: discord.User):
        embed = create_embed(title="User Unbanned", color=0x57F287)
        embed.add_field(name="User", value=str(user), inline=True)
        embed.add_field(name="ID", value=str(user.id), inline=True)
        await self._send_log(guild, embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        embed = create_embed(title="Member Banned", color=ERROR_COLOR)
        embed.add_field(name="User", value=str(user), inline=True)
        embed.add_field(name="ID", value=str(user.id), inline=True)
        await self._send_log(guild, embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        embed = create_embed(title="Member Unbanned", color=0x57F287)
        embed.add_field(name="User", value=str(user), inline=True)
        embed.add_field(name="ID", value=str(user.id), inline=True)
        await self._send_log(guild, embed)

from utils.permissions import has_permissions

async def setup(bot: commands.Bot):
    await bot.add_cog(LoggingCog(bot))
