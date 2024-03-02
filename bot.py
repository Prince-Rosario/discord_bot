import asyncio
import re
import discord
import requests
import json
from discord.ext.commands import Bot
from dotenv import load_dotenv
import os
from typing import Final as fnl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
# import youtube_dl
import yt_dlp
from spotipy.exceptions import SpotifyException

load_dotenv()
TOKEN: fnl[str] = os.getenv('DISCORD_TOKEN')

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.getenv('SPOTIPY_CLIENT_ID'),
                                                           client_secret=os.getenv('SPOTIPY_CLIENT_SECRET')))


def get_meme():
    response = requests.get('https://meme-api.com/gimme')
    json_data = json.loads(response.text)
    return json_data['url']


bot = Bot(command_prefix=os.getenv('DISCORD_PREFIX'), intents=discord.Intents.all())


@bot.event
async def on_ready():
    print('Logged in as {0}!'.format(bot.user))


@bot.command()
async def clear(ctx, limit=100):
    await ctx.channel.purge(limit=limit)
    embed = discord.Embed(title=f'Deleted {limit} messages in this channel.')
    await ctx.send(embed=embed)


@bot.command()
async def hello(ctx):
    await ctx.send('Hello! I am a bot. Type !Help for a list of commands.')


@bot.command()
async def meme(ctx):
    await ctx.send(get_meme())


@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')


@bot.command()
async def join(ctx):
    voice_channel = ctx.author.voice.channel
    vc = await voice_channel.connect()


@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()


@bot.command()
async def playlist(ctx, *, playlist_url):
    # Extract playlist ID from the URL
    match = re.search(r'open\.spotify\.com\/playlist\/([a-zA-Z0-9]+)', playlist_url)
    if match:
        playlist_id = match.group(1)
    else:
        await ctx.send('Invalid Spotify playlist URL.')
        return

    results = sp.playlist(playlist_id)
    print(results)

    tracks = []

    if 'items' in results['tracks']:
        tracks = [item['track'] for item in results['tracks']['items']]
    else:
        await ctx.send('No tracks found in the playlist.')

    voice_channel = ctx.author.voice.channel
    vc = await voice_channel.connect()

    for item in tracks:
        if isinstance(item, dict):
            track_name = item['name']
            track_artist = item['artists'][0]['name']
        else:
            print(f'unexpected track data: {item}')

        ydl_opts = {
            'default_search': 'ytsearch',
            'quiet': True,
            'format': 'bestaudio/best'
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f'{track_name} {track_artist}', download=False)
                if 'formats' in info:
                    best_audio = max(info['entries'][0]['formats'], key=lambda format: format.get('abr', 0))
                    url = best_audio['url']
                else:
                    await ctx.send(f'Error: No formats found for {track_name} by {track_artist} on YouTube.')
                    continue

        except yt_dlp.utils.DownloadError:
            await ctx.send(f'Error: Could not find {track_name} by {track_artist} on YouTube.')
            continue

        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=url))
        while vc.is_playing():
            await asyncio.sleep(1)

    await ctx.send(f'Playing {results["name"]} in {voice_channel}')


@bot.command()
async def play(ctx, *, track):
    voice_channel = ctx.author.voice.channel
    vc = await voice_channel.connect()

    ydl_opts = {
        'default_search': 'ytsearch',  # this instructs yt_dlp to search YouTube
        'format': 'bestaudio/best',  # we only want the best quality audio
        'noplaylist': True,  # we don't want to download a playlist
        'quiet': True  # we don't want verbose output
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f'{track}', download=False)
            if 'entries' in info:
                best_audio = max(info['entries'][0]['formats'], key=lambda format: format.get('abr') or 0)
                url = best_audio['url'] 
                print(url)
            else:
                await ctx.send(f'Error: No formats found for {track} on YouTube.')
                return
    except yt_dlp.utils.DownloadError:
        await ctx.send(f'Error: Could not find {track} on YouTube.')
        return

    source = discord.FFmpegPCMAudio(executable="ffmpeg", source=url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
    vc.play(source)
    await ctx.send(f'Playing {track} in {voice_channel}')

    while vc.is_playing():
        await asyncio.sleep(1)

    
@bot.command()
async def pause(ctx):
    voice_channel = ctx.author.voice.channel
    vc = await voice_channel.connect()
    vc.pause()
    await ctx.send(f'Paused in {voice_channel}')


@bot.command()
async def resume(ctx):
    voice_channel = ctx.author.voice.channel
    vc = await voice_channel.connect()
    vc.resume()
    await ctx.send(f'Resumed in {voice_channel}')


@bot.command()
async def stop(ctx):
    voice_channel = ctx.author.voice.channel
    vc = await voice_channel.connect()
    vc.stop()
    await ctx.send(f'Stopped in {voice_channel}')


@bot.command()
async def Help(ctx):
    embed = discord.Embed(title='Help', description='List of available commands:', color=0x00ff00)
    embed.add_field(name='!hello', value='Greets the user', inline=False)
    embed.add_field(name='!meme', value='Sends a random meme', inline=False)
    embed.add_field(name='!ping', value='Returns the latency', inline=False)
    embed.add_field(name='!clear', value='Clears the chat', inline=False)
    embed.add_field(name='!play', value='Plays a Spotify playlist in the user\'s voice channel', inline=False)
    embed.add_field(name='!join', value='Joins the user\'s voice channel', inline=False)
    embed.add_field(name='!leave', value='Leaves the voice channel', inline=False)
    await ctx.send(embed=embed)


bot.run(TOKEN)
