import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
from utils.helpers import create_embed, success_embed, error_embed
from utils.config import EMBED_COLOR, ERROR_COLOR
from utils.permissions import has_permissions

class SuggestionModal(Modal, title="Submit Suggestion"):
    suggestion = TextInput(label="Suggestion", style=discord.TextStyle.long, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        cog: "SuggestionsCog" = interaction.client.get_cog("SuggestionsCog")
        if cog:
            await cog.submit_suggestion(interaction, str(self.suggestion.value))

class SuggestionView(View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Submit Suggestion", style=discord.ButtonStyle.green, emoji="💡", custom_id="suggest_submit")
    async def submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SuggestionModal())

class SuggestionsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="suggest", description="Submit a suggestion")
    async def suggest(self, ctx: commands.Context, *, suggestion: str):
        embed = create_embed(title="💡 New Suggestion", description=suggestion, color=EMBED_COLOR)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text=f"User ID: {ctx.author.id}")
        view = SuggestionReviewView(self)
        message = await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(name="spanel", description="Send suggestion panel")
    @has_permissions(administrator=True)
    async def panel(self, ctx: commands.Context):
        embed = create_embed(title="💡 Suggestions", description="Click below to submit a suggestion.", color=EMBED_COLOR)
        await ctx.send(embed=embed, view=SuggestionView(self))

    async def submit_suggestion(self, interaction: discord.Interaction, suggestion: str):
        embed = create_embed(title="💡 New Suggestion", description=suggestion, color=EMBED_COLOR)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=success_embed("Suggestion submitted!"), ephemeral=True)
        channel = interaction.guild.get_channel(interaction.channel.id)
        if channel:
            await channel.send(embed=embed)

class SuggestionReviewView(View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, emoji="✅", custom_id="suggest_approve")
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=None)
        await interaction.message.add_reaction("✅")

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red, emoji="❌", custom_id="suggest_reject")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=None)
        await interaction.message.add_reaction("❌")

async def setup(bot: commands.Bot):
    await bot.add_cog(SuggestionsCog(bot))
