import discord
from discord.ext import commands


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.help_message = """
```
General commands:
!help - Displays all available commands
!p <keywords> - finds the song on youtube and plays it in your current channel. Will resume playing the current song if it was paused
!q - displays the current music queue
!skip - skips the current song being played
!clear - Stops the music and clears the queue
!leave - Disconnected the bot from the voice channel
!pause - pauses the current song being played or resumes if already paused
!resume - resumes playing the current song
```
"""
        self.help_embed = discord.Embed(title="Commands", color=discord.Color.green())
        self.help_embed.add_field(
            name="!p [keyword]",
            value="Find the song on youtube and plays it in your current channel. Will resume playing the current song if it was paused",
            inline=True,
        )
        self.text_channel_list = []

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_list.append(channel)
        await self.send_to_all(self.help_message)

    @commands.command(name="help", help="Displays all available commands")
    async def help(self, ctx):
        print("Sending help message")
        await ctx.send(embed=self.help_embed)

    async def send_to_all(self, message):
        print("Sending message to all channels")
        for channel in self.text_channel_list:
            await channel.send(embed=self.help_embed)

    @commands.command(name="test", help="Test command")
    async def test(self, ctx):
        print("Sending test message")
        await ctx.send("Test message")


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
