import discord
from discord.ext import commands
import os
import asyncio

# # import all cogs
# import help_cog
# import music_cog

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), help_command=None)


async def main():

    # load extensions
    await bot.load_extension("help_cog")
    await bot.load_extension("music_cog")

    # cog = bot.get_cog("MusicCog")
    # commands = cog.get_commands()
    # print([c.name for c in commands])

    # start the bot with our token
    await bot.start(os.getenv("TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())
