import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput
from utils.helpers import create_embed, success_embed, error_embed
from utils.config import EMBED_COLOR, ERROR_COLOR
from utils.permissions import has_permissions

class ReportModal(Modal, title="Report User"):
    reason = TextInput(label="Reason", style=discord.TextStyle.long, required=True, placeholder="Why are you reporting this user?")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        embed = create_embed(
            title="🚨 User Report",
            description=str(self.reason.value),
            color=ERROR_COLOR
        )
        embed.add_field(name="Reported User", value=interaction.user.mention, inline=True)
        embed.set_footer(text=f"User ID: {interaction.user.id}")
        log_channel = interaction.guild.get_channel(interaction.channel.id)
        if log_channel:
            await log_channel.send(embed=embed)
        await interaction.followup.send(embed=success_embed("Report submitted to staff."), ephemeral=True)

class ReportsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="report", description="Report a user")
    async def report(self, ctx: commands.Context, member: discord.Member):
        if member.bot:
            await ctx.send(embed=error_embed("You cannot report bots."))
            return
        await ctx.send_modal(ReportModal())

    @commands.hybrid_command(name="reportmsg", description="Report a message")
    async def report_message(self, ctx: commands.Context, message_id: str):
        try:
            message_id_int = int(message_id)
        except ValueError:
            await ctx.send(embed=error_embed("Invalid message ID."))
            return
        try:
            message = await ctx.channel.fetch_message(message_id_int)
        except Exception:
            await ctx.send(embed=error_embed("Message not found in this channel."))
            return
        embed = create_embed(title="🚨 Reported Message", color=ERROR_COLOR)
        embed.add_field(name="Content", value=message.content or "*No text content*", inline=False)
        embed.add_field(name="Author", value=message.author.mention, inline=True)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        embed.add_field(name="Reported by", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ReportsCog(bot))
