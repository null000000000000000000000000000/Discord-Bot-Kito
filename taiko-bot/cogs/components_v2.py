import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Select
from utils.helpers import create_embed
from utils.config import EMBED_COLOR

class ComponentsV2Cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="v2demo", description="Demo Discord Components V2")
    async def v2_demo(self, ctx: commands.Context):
        view = View(timeout=180)

        class DemoButton(Button):
            async def callback(self, interaction: discord.Interaction):
                await interaction.response.send_message("You clicked a V2 button!", ephemeral=True)

        class DemoSelect(Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="Option A", value="a", description="First option"),
                    discord.SelectOption(label="Option B", value="b", description="Second option"),
                ]
                super().__init__(placeholder="Select an option...", options=options, custom_id="demo_select")

            async def callback(self, interaction: discord.Interaction):
                await interaction.response.send_message(f"You selected: {self.values[0]}", ephemeral=True)

        view.add_item(DemoButton(label="Click Me", style=discord.ButtonStyle.blurple))
        view.add_item(DemoButton(label="Danger", style=discord.ButtonStyle.red))
        view.add_item(DemoSelect())

        embed = create_embed(
            title="Components V2 Demo",
            description="This demonstrates modern Discord UI components.",
            color=EMBED_COLOR
        )
        await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(name="sectiondemo", description="Demo Section component")
    async def section_demo(self, ctx: commands.Context):
        embed = create_embed(
            title="Section Demo",
            description="Sections organize content with accessory components.",
            color=EMBED_COLOR
        )
        embed.add_field(name="Section 1", value="Content inside a section", inline=False)
        embed.add_field(name="Section 2", value="More content", inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="mediademo", description="Demo Media Gallery")
    async def media_demo(self, ctx: commands.Context):
        embed = create_embed(
            title="Media Gallery Demo",
            description="Display multiple images in a gallery format.",
            color=EMBED_COLOR
        )
        embed.set_image(url="https://via.placeholder.com/400x200/5865F2/FFFFFF?text=Media+1")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="textdisplay", description="Demo Text Display")
    async def text_display(self, ctx: commands.Context):
        content = (
            "**Text Display Component**\n"
            "This is a standalone text display block.\n"
            "Supports markdown formatting."
        )
        await ctx.send(content)

async def setup(bot: commands.Bot):
    await bot.add_cog(ComponentsV2Cog(bot))
