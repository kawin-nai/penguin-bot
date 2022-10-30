import json
import discord
import datetime
from discord.ext import commands
import asyncio
import cred

from youtube_dl import YoutubeDL
from spotipy import Spotify, SpotifyOAuth


def get_songs_from_spotify(spotify, playlist_id):
    try:
        results = spotify.playlist_items(playlist_id)
        songs = results["items"]
        while results["next"]:
            results = spotify.next(results)
            songs.extend(results["items"])
        # Print the title of the playlist
        # print(results["items"][0]["added_by"]["display_name"])
        print(f"Playlist name: {results['items'][0]['added_by']['id']}")

        # Print the first 20 songs in the playlist
        for i, item in enumerate(songs):
            track = item["track"]
            print("   %d %32.32s %s" % (i, track["artists"][0]["name"], track["name"]))
        return songs
    except Exception as e:
        print(e)
        return None


spotify = Spotify(auth_manager=SpotifyOAuth(client_id=cred.client_id, client_secret=cred.client_secret,
                                            redirect_uri=cred.redirect_uri, scope=cred.scope))
spotify_songs = get_songs_from_spotify(spotify,
                                       "https://open.spotify.com/playlist/0sPCnHX7KDgox24y79jNTM?si=8fce20b341b84e6e")
