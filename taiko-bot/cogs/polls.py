import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from utils.helpers import create_embed, success_embed, error_embed
from utils.config import EMBED_COLOR, ERROR_COLOR
from utils.permissions import has_permissions

class PollButton(Button):
    def __init__(self, label: str, poll_id: int, option_index: int):
        super().__init__(label=label, style=discord.ButtonStyle.blurple, custom_id=f"poll_{poll_id}_{option_index}")
        self.poll_id = poll_id
        self.option_index = option_index

    async def callback(self, interaction: discord.Interaction):
        cog: "PollsCog" = interaction.client.get_cog("PollsCog")
        if not cog:
            await interaction.response.send_message("Poll system unavailable.", ephemeral=True)
            return
        poll = cog._polls.get(self.poll_id)
        if not poll:
            await interaction.response.send_message("Poll not found.", ephemeral=True)
            return
        votes = poll["votes"]
        user_votes = votes.setdefault(str(interaction.user.id), [])
        if self.option_index in user_votes:
            user_votes.remove(self.option_index)
            action = "removed vote from"
        else:
            user_votes.append(self.option_index)
            action = "voted for"
        await interaction.response.send_message(f"You {action} **{poll['options'][self.option_index]}**", ephemeral=True)

class PollsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._polls: dict[int, dict] = {}
        self._next_id = 1

    @commands.hybrid_command(name="poll", description="Create a poll")
    @has_permissions(administrator=True)
    async def create_poll(self, ctx: commands.Context, question: str, option1: str, option2: str, option3: str | None = None, option4: str | None = None):
        options = [option1, option2]
        if option3:
            options.append(option3)
        if option4:
            options.append(option4)
        if len(options) < 2:
            await ctx.send(embed=error_embed("You must provide at least 2 options."))
            return
        poll_id = self._next_id
        self._next_id += 1
        self._polls[poll_id] = {
            "question": question,
            "options": options,
            "votes": {},
        }
        view = View(timeout=None)
        for i, opt in enumerate(options):
            view.add_item(PollButton(opt[:80], poll_id, i))
        embed = create_embed(title=f"📊 Poll: {question}", color=EMBED_COLOR)
        embed.add_field(name="Options", value="\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)]), inline=False)
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(PollsCog(bot))
