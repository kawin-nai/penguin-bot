import discord
from discord.ext import commands
import os
import asyncio


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), help_command=None)


async def main():

    # load extensions
    await bot.load_extension("help_cog")
    await bot.load_extension("music_cog")
    # await bot.load_extension("spotify_cog")

    # start the bot with our token
    await bot.start(os.getenv("TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())
