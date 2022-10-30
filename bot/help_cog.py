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
        self.help_embed = discord.Embed(
            title="Commands",
            description="Please make sure you're connected to a voice channel before typing!",
            color=discord.Color.green(),
        )
        self.help_embed.add_field(
            name="!p [keyword, spotify playlist link]",
            value="Finds the song on youtube or spotify playlist and plays it in your current channel.",
            inline=False,
        )
        self.help_embed.add_field(
            name="!skip, !s",
            value="Skips the current song",
            inline=False,
        )
        self.help_embed.add_field(
            name="!sw [song_no]",
            value="Skips to the song number in the queue",
            inline=False,
        )
        self.help_embed.add_field(
            name="!sh",
            value="Shuffles the music queue",
            inline=False,
        )
        self.help_embed.add_field(
            name="!queue, !q",
            value="Displays the top six songs in the music queue",
            inline=False,
        )
        self.help_embed.add_field(
            name="!queue_all, !qa",
            value="Displays the current music queue",
            inline=False,
        )
        self.help_embed.add_field(
            name="!clear",
            value="Stops the music and clears the queue",
            inline=False,
        )
        self.help_embed.add_field(
            name="!leave, !d",
            value="Disconnects the bot from the voice channel",
            inline=False,
        )
        self.help_embed.add_field(
            name="!pause",
            value="Pauses or resumes the current song",
            inline=False,
        )
        self.help_embed.add_field(
            name="!help",
            value="Displays this message",
            inline=False,
        )
        self.text_channel_list = []

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_list.append(channel)
        print("Bot is ready")
        # print(self.text_channel_list)
        # await self.help_to_all()

    @commands.command(name="help", help="Displays all available commands")
    async def help(self, ctx):
        print("Sending help message")
        await ctx.send(embed=self.help_embed)

    async def help_to_all(self):
        print("Sending help message to all general channels")
        for channel in self.text_channel_list:
            if channel.name == "general":
                await channel.send(embed=self.help_embed)

    @commands.command(name="test", help="Test command")
    async def test(self, ctx):
        print("Sending test message")
        await ctx.send("Test message")

    @commands.command(name="send_message", aliases=["m"], help="Messages to all channels")
    async def send_message(self, ctx, *args):
        message = " ".join(args)
        # print(message)
        for channel in self.text_channel_list:
            if channel.name == "general":
                await channel.send(message)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
