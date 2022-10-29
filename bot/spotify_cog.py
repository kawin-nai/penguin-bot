import json
import discord
import datetime
from discord.ext import commands
import asyncio

from youtube_dl import YoutubeDL


class SpotifyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # all the music related stuff
        self.is_playing = False
        self.is_paused = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        self.vc = None


    def play_next(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            # get the first url
            song = self.music_queue[0][0]
            voice_channel = self.music_queue[0][1]
            m_url = self.music_queue[0][0]["source"]
            self.cursong = song
            print("Cursong in play_next: ", self.cursong["title"])
            # remove the first element as you are currently playing it
            self.music_queue.pop(0)

            embed = discord.Embed(
                title="Now Playing",
                url=song["weburl"],
                description=song["title"],
                color=discord.Color.blurple(),
            )
            # minutes, seconds = divmod(song["duration"], 60)
            embed.set_footer(text="Duration [%s]" % song["duration"])

            coro = ctx.send(embed = embed)
            fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
            try:
                fut.result()
            except:
                pass

            self.vc.play(
                discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), 0.7),
                after=lambda e: self.play_next(ctx),
            )
        else:
            self.is_playing = False

    # infinite loop checking
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            song = self.music_queue[0][0]
            m_url = self.music_queue[0][0]["source"]
            self.cursong = song
            print("Cursong in play_music: ", self.cursong["title"])

            # try to connect to voice channel if you are not already connected
            if self.vc is None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                # in case we fail to connect
                if self.vc is None:
                    await ctx.send("Could not connect to the voice channel")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            # remove the first element as you are currently playing it
            self.music_queue.pop(0)

            if song["raw_duration"] > 1200:
                error_embed = discord.Embed(
                    title="Error: Song is too long",
                    description="The song you requested is too long. Please request a song that is less than 20 minutes.",
                    color=discord.Color.red(),
                )
                error_embed.set_footer(text="Duration [%s]" % song["duration"])
                await ctx.send(embed=error_embed)
                self.is_playing = False
                return

            print("In play_music, building embed")
            embed = discord.Embed(
                title="Now Playing",
                url=song["weburl"],
                description=song["title"],
                color=discord.Color.blurple(),
            )
            # embed.add_field(name="", value=song["title"](song["weburl"]))
            # minutes, seconds = divmod(song["duration"], 60)
            embed.set_footer(text="Duration [%s]" % song["duration"])
            await ctx.send(embed=embed)
            print("In play_music, embed sent")

            self.vc.play(
                discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), 0.7),
                after=lambda e: self.play_next(ctx),
            )
        else:
            self.is_playing = False

    @commands.command(
        name="play_spotify", aliases=["ps"], help="Plays a selected song from Spotify"
    )
    async def play_spotify(self, ctx, *args):
        query = " ".join(args)
        print("Searching for: %s" % query)
        # print("Message: ", ctx.author, ctx.author.status, ctx.author.voice.channel)
        voice_channel = ctx.author.voice.channel
        # print("No voice", voice_channel)
        if voice_channel is None:
            # you need to be connected so that the bot knows where to go
            print("No voice")
            await ctx.send("Connect to a voice channel!")
            return
        elif self.is_paused:
            print("resume??")
            self.vc.resume()
        else:
            self.is_playing = True
            # Get song url
            print("Successfully enter the !p command")
            # song_url = "https://www.youtube.com/watch?v=" + song["weburl"]
            # print(song)
            embed = discord.Embed(
                title="Test",
                description="Added to queue",
                color=discord.Color.green(),
            )

            self.vc.play(
                discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), 0.7),
            )


    @commands.command(
        name="skip_spotify", aliases=["ss"], help="Skips the current song being played"
    )
    async def skip_spotify(self, ctx):
        if self.vc is not None and self.vc:
            print("Skipping song")
            print("Cursong in skip: ", self.cursong["title"])
            self.vc.stop()
            embed = discord.Embed(
                title="Skipped",
                color=discord.Color.blue(),
            )
            await ctx.send(embed=embed)
            # try to play next in the queue if it exists
            # await self.play_music(ctx)

    @commands.command(
        name="queue_spotify", aliases=["qs"], help="Displays the current songs in queue"
    )
    async def queue_spotify(self, ctx):
        retval = ""
        if self.cursong is None:
            await ctx.send(
                embed=discord.Embed(
                    title="Queue is empty",
                    color=discord.Color.red(),
                )
            )
            return
        embed = discord.Embed(
            title="Queue",
            description="Current songs in queue",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="Playing - " + self.cursong["title"],
            value="Duration [%s]" % self.cursong["duration"],
            inline=False,
        )
        for i in range(0, len(self.music_queue)):
            # display a max of 5 songs in the current queue
            if i > 4:
                break
            retval += self.music_queue[i][0]["title"] + "\n"
            embed.add_field(
                name=str(i + 1) + ". " + self.music_queue[i][0]["title"],
                value="Duration [%s]" % self.music_queue[i][0]["duration"],
                inline=False,
            )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SpotifyCog(bot))
