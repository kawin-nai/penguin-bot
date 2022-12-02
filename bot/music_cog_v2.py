import logging
import os
from asyncio import CancelledError

import discord
import datetime
from discord.ext import commands
import asyncio
import random

from youtube_dl import YoutubeDL
from spotipy import Spotify, SpotifyClientCredentials


class MusicCogV2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spotify = Spotify(
            auth_manager=SpotifyClientCredentials(client_id=os.getenv("SPOTIFY_ID"), client_secret=os.getenv("SPOTIFY_SECRET")))
        # all the music related stuff
        self.is_playing = False
        self.is_paused = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        self.vc = None
        self.cursong = None
        logging.basicConfig(level=logging.DEBUG)

    # Check if the bot is inactive for more than 60 minutes and disconnect itself.
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.id == self.bot.user.id:
            return
        if after.channel is None:
            return
        voice = after.channel.guild.voice_client
        time = 0
        while True:
            await asyncio.sleep(1)
            time += 1
            if not voice.is_connected():
                break
            if voice.is_playing():
                time = 0
            if time > 3600:
                await voice.disconnect()
                break

    # Search the song on youtube and return the url
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch: %s" % item, download=False)
                if "entries" in info:
                    info = info["entries"][0]
                # print("Info: ", info)
            except Exception as e:
                print(e)
                return None

        # pretty print and save to json file
        # print(json.dumps(info, indent=2))
        # with open("song.json", "w") as f:
        #     json.dump(info, f, indent=2)
        duration = str(datetime.timedelta(seconds=info["duration"]))
        return {
            "source": info["formats"][0]["url"],
            "title": info["title"],
            "weburl": info["webpage_url"],
            "duration": duration,
            "raw_duration": info["duration"],
        }

    def get_songs_from_spotify(self, playlist_id):
        try:
            logging.info("Getting songs from spotify playlist")
            results = self.spotify.playlist_items(playlist_id)
            songs = results["items"]
            while results["next"]:
                results = self.spotify.next(results)
                songs.extend(results["items"])
            logging.info("Got songs from spotify playlist")
            return songs
        except Exception as e:
            print(e)
            return None

    def play_next(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            # get the first url
            song = self.search_yt(self.music_queue[0][0])
            m_url = song["source"]
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

            coro = ctx.send(embed=embed)
            fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
            try:
                fut.result()
            except (TimeoutError, CancelledError):
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

            song = self.search_yt(self.music_queue[0][0])

            # if type(song) == type(True):
            #     print("Wrong song bro")
            #     embed = discord.Embed(
            #         title="Could not download the song",
            #         description="Try a different keyword",
            #         color=discord.Color.red(),
            #     )
            #     await ctx.send(embed=embed)
            #     self.music_queue.pop(0)
            m_url = song["source"]

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

            # if song["raw_duration"] > 600:
            #     error_embed = discord.Embed(
            #         title="Error: Song is too long",
            #         description="The song you requested is too long. Please request a song that is less than 20 minutes.",
            #         color=discord.Color.red(),
            #     )
            #     error_embed.set_footer(text="Duration [%s]" % song["duration"])
            #     await ctx.send(embed=error_embed)
            #     self.is_playing = False
            #     return

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
        name="play", aliases=["p", "playing"], help="Plays a selected song from youtube"
    )
    async def play(self, ctx, *args):
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
            print("Resume")
            self.vc.resume()
        else:
            if "spotify" in query:
                print("Querying spotify playlist")
                # get the song list from spotify playlist
                songs = self.get_songs_from_spotify(query)
                random.shuffle(songs)
                playlist_detail = self.spotify.playlist(query)

                for i, song in enumerate(songs):
                    track = song["track"]
                    artist = track["artists"][0]["name"]
                    title = track["name"]
                    yt_query = "%s %s audio" % (artist, title)
                    # song_result = self.search_yt("%s %s audio" % (artist, title))
                    self.music_queue.append([yt_query, voice_channel, ctx.author])
                    # self.music_queue.append(["%s %s audio" % (artist, title), voice_channel])
                    if i == 0 and not self.is_playing:
                        await self.play_music(ctx)
                print("Finish querying spotify playlist")
                embed = discord.Embed(
                    title="Playlist - %s by %s" % (playlist_detail["name"], playlist_detail["owner"]["display_name"]),
                    url=query,
                    description="Added to queue",
                    color=discord.Color.green(),
                )

                embed.set_footer(text="Playlist items: %d" % len(songs))
                await ctx.send(embed=embed)
                await self.queue(ctx)

            else:
                # Get song url
                print("Successfully enter the !p command")

                embed = discord.Embed(
                    title="Query submitted",
                    color=discord.Color.green()
                )
                # minutes, seconds = divmod(song["duration"], 60)
                # embed.set_footer(text="Duration [%s]" % song["duration"])
                await ctx.send(embed=embed)

                self.music_queue.append([query, voice_channel, ctx.author])

                if not self.is_playing:
                    await self.play_music(ctx)

    @commands.command(name="play_next", aliases=["pn"], help="Plays a selected song from youtube next in queue")
    async def play_next_in_queue(self, ctx, *args):
        if self.vc is None or not self.vc.is_connected():
            await ctx.send("Connect to a voice channel!")
            return
        if self.is_paused:
            self.vc.resume()
        if len(self.music_queue) == 0:
            await self.play(ctx, *args)
            return
        query = " ".join(args)
        embed = discord.Embed(
            title="Query submitted",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        voice_channel = ctx.author.voice.channel
        self.music_queue.insert(0, [query, voice_channel, ctx.author])

    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(
        name="resume", aliases=["r"], help="Resumes playing with the discord bot"
    )
    async def resume(self, ctx):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(
        name="skip", aliases=["s"], help="Skips the current song being played"
    )
    async def skip(self, ctx):
        if self.vc is not None and self.vc:
            print("Skipping song")
            print("Cursong in skip: ", self.cursong["title"])
            self.vc.stop()
            embed = discord.Embed(
                title="Skipped",
                color=discord.Color.blue(),
            )
            await ctx.send(embed=embed)

    @commands.command(
        name="switch_to", aliases=["sw"], help="Skip the current song and switch to a different song in the queue"
    )
    async def switch_to(self, ctx, *args):
        if self.vc is None or not self.vc.is_connected():
            await ctx.send("Connect to a voice channel!")
            return

        song_no = int(args[0])
        if song_no > len(self.music_queue):
            embed = discord.Embed(
                title="Song number is out of range",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return
        print("Switching song")
        # Rearrange music queue
        self.music_queue.insert(0, self.music_queue.pop(song_no - 1))
        self.vc.stop()
        embed = discord.Embed(
            title="Switch to song #%d" % song_no,
            color=discord.Color.blue(),
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="shuffle", aliases=["sh"], help="Shuffle the music queue"
    )
    async def shuffle(self, ctx):
        if self.vc is not None and self.vc:
            if len(self.music_queue) <= 1:
                embed = discord.Embed(
                    title="Not enough songs in the queue",
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return
            print("Shuffling song")
            # Shuffle music queue
            random.shuffle(self.music_queue)

            embed = discord.Embed(
                title="Shuffled",
                color=discord.Color.blue(),
            )
            await ctx.send(embed=embed)
            await self.queue(ctx)

    @commands.command(
        name="queue", aliases=["q", "list"], help="Displays the top 8 songs in queue"
    )
    async def queue(self, ctx):
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
            # display a max of 6 songs in the current queue
            if i > 5:
                break
            if self.music_queue[i][0].endswith("audio"):
                embed.add_field(
                    name=str(i + 1) + ". " + self.music_queue[i][0][:-5],
                    value="Requested by: " + self.music_queue[i][2].name,
                    inline=False,
                )
            else:
                embed.add_field(
                    name=str(i + 1) + ". " + self.music_queue[i][0],
                    value="Requested by: " + self.music_queue[i][2].name,
                    inline=False,
                )
        if len(self.music_queue) > 6:
            embed.add_field(name="...", value="...", inline=False)
        embed.set_footer(text="Total songs in queue: %d" % len(self.music_queue))
        await ctx.send(embed=embed)

    @commands.command(
        name="queue_all", aliases=["qa", "listall"], help="Displays all songs in queue"
    )
    async def queue_all(self, ctx):
        if self.cursong is None:
            await ctx.send(
                embed=discord.Embed(
                    title="Queue is empty",
                    color=discord.Color.red(),
                )
            )
            return

        message = "Current songs in queue\n"
        for i in range(0, min(20, len(self.music_queue))):
            message += str(i + 1) + ". " + self.music_queue[i][0] + " (" + "Requested by:  " + self.music_queue[i][
                2].name + "\n"
        if len(self.music_queue) > 20:
            message += "..."
        message += "\nTotal songs in queue: %d" % len(self.music_queue)
        await ctx.send(message)
        # embed.set_footer(text="Total songs in queue: %d" % len(self.music_queue))
        # await ctx.send(embed=embed)

    @commands.command(
        name="clear", aliases=["c", "bin"], help="Stops the music and clears the queue"
    )
    async def clear(self, ctx):
        if self.vc is not None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Music queue cleared")

    @commands.command(
        name="leave", aliases=["disconnect", "l", "d"], help="Kick the bot from VC"
    )
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.clear(ctx)
        await self.vc.disconnect()


async def setup(bot):
    await bot.add_cog(MusicCogV2(bot))
