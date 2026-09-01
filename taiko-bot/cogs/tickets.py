import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
from sqlalchemy.future import select
from database.manager import get_session
from database.models import Ticket
from utils.helpers import create_embed, success_embed, error_embed
from utils.config import EMBED_COLOR, ERROR_COLOR
from utils.permissions import has_permissions

class TicketModal(Modal, title="Create Ticket"):
    category = TextInput(label="Category", placeholder="support, bug, report", required=False)
    subject = TextInput(label="Subject", placeholder="Brief description of your issue", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        cog = interaction.client.get_cog("TicketsCog")
        if cog:
            await cog.create_ticket(interaction, str(self.category.value), str(self.subject.value))

class TicketControlView(View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red, emoji="🔒", custom_id="ticket_close")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = interaction.client.get_cog("TicketsCog")
        if cog:
            await interaction.response.send_message("Closing ticket...")
            await interaction.channel.send(embed=success_embed("Ticket closed."))
            await interaction.channel.edit(overwrites={interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False)})
            cog._open_tickets.pop(interaction.channel.id, None)
            async with get_session() as session:
                result = await session.execute(select(Ticket).where(Ticket.channel_id == interaction.channel.id))
                ticket = result.scalar_one_or_none()
                if ticket:
                    ticket.status = "closed"
                    await session.commit()
        else:
            await interaction.response.send_message("Could not find ticket cog.", ephemeral=True)

class TicketView(View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.green, emoji="📩", custom_id="ticket_create")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketModal())

class TicketsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._open_tickets: dict[int, discord.TextChannel] = {}

    async def _get_or_create_category(self, guild: discord.Guild) -> discord.CategoryChannel | None:
        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            try:
                category = await guild.create_category("Tickets")
            except Exception:
                return None
        return category

    async def create_ticket(self, interaction: discord.Interaction, category: str, subject: str):
        guild = interaction.guild
        user = interaction.user
        cat = await self._get_or_create_category(guild)
        if not cat:
            await interaction.followup.send(embed=error_embed("Could not create ticket category."), ephemeral=True)
            return
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
        }
        staff_role = discord.utils.get(guild.roles, name="Staff")
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        try:
            channel = await guild.create_text_channel(
                name=f"ticket-{user.name}",
                category=cat,
                overwrites=overwrites,
                reason=f"Ticket by {user}"
            )
        except Exception:
            await interaction.followup.send(embed=error_embed("Failed to create ticket channel."), ephemeral=True)
            return
        async with get_session() as session:
            ticket = Ticket(guild_id=guild.id, channel_id=channel.id, user_id=user.id, category=category or "general")
            session.add(ticket)
            await session.commit()
            await session.refresh(ticket)
        self._open_tickets[channel.id] = channel
        embed = create_embed(
            title=f"Ticket #{ticket.id}",
            description=f"Category: {category or 'general'}\nSubject: {subject}\nCreated by: {user.mention}",
            color=EMBED_COLOR
        )
        view = TicketControlView(self)
        await channel.send(embed=embed, view=view)
        await interaction.followup.send(embed=success_embed(f"Ticket created: {channel.mention}"), ephemeral=True)

    @commands.hybrid_command(name="close", description="Close the current ticket")
    async def close(self, ctx: commands.Context):
        if ctx.channel.id not in self._open_tickets:
            await ctx.send(embed=error_embed("This is not a ticket channel."))
            return
        await ctx.send(embed=success_embed("Ticket will be closed in 5 seconds..."))
        await ctx.channel.edit(overwrites={ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False)})
        await ctx.channel.set_permissions(ctx.author, view_channel=False)
        self._open_tickets.pop(ctx.channel.id, None)
        async with get_session() as session:
            result = await session.execute(select(Ticket).where(Ticket.channel_id == ctx.channel.id))
            ticket = result.scalar_one_or_none()
            if ticket:
                ticket.status = "closed"
                await session.commit()

    @commands.hybrid_command(name="panel", description="Send the ticket creation panel")
    @has_permissions(administrator=True)
    async def panel(self, ctx: commands.Context):
        embed = create_embed(
            title="Support Tickets",
            description="Click the button below to create a ticket.",
            color=EMBED_COLOR
        )
        await ctx.send(embed=embed, view=TicketView(self))

async def setup(bot: commands.Bot):
    await bot.add_cog(TicketsCog(bot))
