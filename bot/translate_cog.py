import discord
from discord.ext import commands
import googletrans


class TranslateCog(discord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator = googletrans.Translator()

    @commands.command(name="translate", aliases=["tr"])
    async def translate(self, ctx, *args):
        message = " ".join(args)
        try:
            result = self.translator.translate(message, dest="th")
            await ctx.send(result.text)
        except ValueError:
            await ctx.send("Error: Invalid translation")

    @commands.command(name="thai", aliases=["th"])
    async def translate(self, ctx, *args):
        message = " ".join(args)
        try:
            result = self.translator.translate(message, dest="en")
            await ctx.send(result.text)
        except ValueError:
            await ctx.send("Error: Invalid translation")


async def setup(bot):
    await bot.add_cog(TranslateCog(bot))
