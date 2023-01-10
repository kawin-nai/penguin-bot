import discord
from discord.ext import commands
import logging


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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
            name="!pn [keyword]",
            value="Finds the song on youtube and puts it next in queue.",
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
            name="!leave, !d, !l",
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
        self.help_embed.add_field(
            name="!define, !def [word]",
            value="Displays the definition of the word",
            inline=False,
        )
        self.help_embed.add_field(
            name="!translate, !tr [sentence]",
            value="Translate the English sentence to Thai",
            inline=False,
        )
        self.text_channel_list = []

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_list.append(channel)
        logging.info("Bot is ready")
        # logging.info(self.text_channel_list)
        # await self.help_to_all()

    @commands.command(name="help", help="Displays all available commands")
    async def help(self, ctx):
        logging.info("Sending help message")
        await ctx.send(embed=self.help_embed)

    async def help_to_all(self):
        logging.info("Sending help message to all general channels")
        for channel in self.text_channel_list:
            if channel.name == "general":
                await channel.send(embed=self.help_embed)

    @commands.command(name="test", help="Test command")
    async def test(self, ctx):
        logging.info("Sending test message")
        await ctx.send("Test message")

    @commands.command(name="send_message", aliases=["m"], help="Messages to all channels")
    async def send_message(self, ctx, *args):
        message = " ".join(args)
        # logging.info(message)
        for channel in self.text_channel_list:
            if channel.name == "general":
                await channel.send(message)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
