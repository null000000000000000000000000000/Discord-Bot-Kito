import random
import discord
from discord.ext import commands
from utils.helpers import create_embed, error_embed
from utils.config import EMBED_COLOR, ERROR_COLOR

class FunCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="8ball", description="Ask the magic 8ball")
    async def eightball(self, ctx: commands.Context, *, question: str):
        responses = [
            "It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.",
            "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.",
            "Signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
            "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "My reply is no.",
            "My sources say no.", "Outlook not so good.", "Very doubtful."
        ]
        embed = create_embed(title="🎱 Magic 8-Ball", color=EMBED_COLOR)
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=random.choice(responses), inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="coinflip", description="Flip a coin")
    async def coinflip(self, ctx: commands.Context):
        result = random.choice(["Heads", "Tails"])
        embed = create_embed(title="🪙 Coin Flip", description=f"Result: **{result}**", color=EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="dice", description="Roll a dice")
    async def dice(self, ctx: commands.Context, sides: int = 6):
        if sides < 2:
            await ctx.send(embed=error_embed("Dice must have at least 2 sides."))
            return
        result = random.randint(1, sides)
        embed = create_embed(title="🎲 Dice Roll", description=f"**{sides}**-sided dice: **{result}**", color=EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="choose", description="Let the bot choose between options")
    async def choose(self, ctx: commands.Context, *, options: str):
        choices = [opt.strip() for opt in options.split(",") if opt.strip()]
        if len(choices) < 2:
            await ctx.send(embed=error_embed("Please provide at least 2 options separated by commas."))
            return
        choice = random.choice(choices)
        embed = create_embed(title="🤔 Choice", description=f"I choose: **{choice}**", color=EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="rate", description="Rate something")
    async def rate(self, ctx: commands.Context, *, thing: str):
        rating = random.randint(1, 10)
        embed = create_embed(title="⭐ Rating", description=f"I rate **{thing}** a **{rating}/10**", color=EMBED_COLOR)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="joke", description="Tell a random joke")
    async def joke(self, ctx: commands.Context):
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs.",
            "Why did the developer go broke? Because he used up all his cache.",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
            "Why do Java developers wear glasses? Because they don't C#.",
            "I told my computer I needed a break, and it said 'No problem, I'll go to sleep.'",
        ]
        await ctx.send(embed=create_embed(title="😂 Joke", description=random.choice(jokes), color=EMBED_COLOR))

    @commands.hybrid_command(name="meme", description="Get a random meme")
    async def meme(self, ctx: commands.Context):
        memes = [
            "When the code works on the first try: 🚩",
            "Programmer: 'It works on my machine'",
            "git push --force",
            "It's not a bug, it's a feature.",
            "There are only 10 types of people: those who understand binary and those who don't.",
        ]
        await ctx.send(embed=create_embed(title="📸 Meme", description=random.choice(memes), color=EMBED_COLOR))

    @commands.hybrid_command(name="ship", description="Ship two users")
    async def ship(self, ctx: commands.Context, user1: discord.Member, user2: discord.Member):
        compatibility = random.randint(0, 100)
        if compatibility > 80:
            emoji = "💞"
            text = "Perfect match!"
        elif compatibility > 50:
            emoji = "💖"
            text = "Good match!"
        else:
            emoji = "💔"
            text = "It's complicated..."
        embed = create_embed(
            title=f"{emoji} Ship",
            description=f"**{user1.display_name}** + **{user2.display_name}**\nCompatibility: **{compatibility}%**\n{text}",
            color=EMBED_COLOR
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="random", description="Pick a random user")
    async def random_user(self, ctx: commands.Context):
        if not ctx.guild:
            await ctx.send(embed=error_embed("This command can only be used in a server."))
            return
        member = random.choice(ctx.guild.members)
        await ctx.send(embed=create_embed(title="🎲 Random User", description=f"Selected: **{member.mention}**", color=EMBED_COLOR))

async def setup(bot: commands.Bot):
    await bot.add_cog(FunCog(bot))
