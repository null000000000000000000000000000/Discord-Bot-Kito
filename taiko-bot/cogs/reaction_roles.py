import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Select
from utils.helpers import create_embed, success_embed, error_embed
from utils.config import EMBED_COLOR, ERROR_COLOR
from utils.permissions import has_permissions

class RoleButton(Button):
    def __init__(self, role_id: int, label: str, style: discord.ButtonStyle = discord.ButtonStyle.blurple):
        super().__init__(label=label, style=style, custom_id=f"role_{role_id}")
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message("Role not found.", ephemeral=True)
            return
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role, reason="Reaction role")
            await interaction.response.send_message(f"Removed {role.mention}", ephemeral=True)
        else:
            await interaction.user.add_roles(role, reason="Reaction role")
            await interaction.response.send_message(f"Added {role.mention}", ephemeral=True)

class ReactionRolesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="rrpanel", description="Create a reaction role panel")
    @has_permissions(manage_roles=True)
    async def rr_panel(self, ctx: commands.Context, role1: discord.Role, label1: str, role2: discord.Role | None = None, label2: str | None = None):
        view = View(timeout=None)
        view.add_item(RoleButton(role1.id, label1 or role1.name))
        if role2 and label2:
            view.add_item(RoleButton(role2.id, label2 or role2.name))
        embed = create_embed(title="Reaction Roles", description="Click a button to toggle your role.", color=EMBED_COLOR)
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(ReactionRolesCog(bot))
