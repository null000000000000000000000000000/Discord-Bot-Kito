import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import create_embed, error_embed
from utils.config import EMBED_COLOR, ERROR_COLOR
from utils.permissions import has_permissions
import aiohttp

class AICog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._conversations: dict[int, list[dict]] = {}
        self._api_key: str | None = None

    async def _get_api_key(self) -> str | None:
        if not self._api_key:
            from utils.config import os
            self._api_key = os.getenv("GROQ_API_KEY")
        return self._api_key

    @commands.hybrid_command(name="ai", description="Chat with the AI assistant")
    async def chat(self, ctx: commands.Context, *, message: str):
        api_key = await self._get_api_key()
        if not api_key:
            await ctx.send(embed=error_embed("AI is not configured. Set GROQ_API_KEY in .env"))
            return
        await ctx.defer()
        user_id = ctx.author.id
        if user_id not in self._conversations:
            self._conversations[user_id] = []
        self._conversations[user_id].append({"role": "user", "content": message})
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={
                        "model": "llama3-8b-8192",
                        "messages": self._conversations[user_id],
                        "max_tokens": 500,
                    }
                ) as resp:
                    data = await resp.json()
                    reply = data["choices"][0]["message"]["content"]
        except Exception as e:
            await ctx.send(embed=error_embed(f"AI request failed: {str(e)}"))
            return
        self._conversations[user_id].append({"role": "assistant", "content": reply})
        if len(self._conversations[user_id]) > 20:
            self._conversations[user_id] = self._conversations[user_id][-20:]
        await ctx.send(reply)

    @commands.hybrid_command(name="aiclear", description="Clear your AI conversation history")
    async def clear_history(self, ctx: commands.Context):
        self._conversations.pop(ctx.author.id, None)
        await ctx.send(embed=success_embed("Conversation history cleared."))

    @commands.hybrid_command(name="aisetup", description="Configure AI settings")
    @has_permissions(administrator=True)
    async def setup_ai(self, ctx: commands.Context, api_key: str):
        self._api_key = api_key
        await ctx.send(embed=success_embed("AI API key configured."))

async def setup(bot: commands.Bot):
    await bot.add_cog(AICog(bot))
