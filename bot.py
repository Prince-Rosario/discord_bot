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
from discord.ext import commands 
from discord.ext import menus
import sqlite3

import valorant

load_dotenv()
TOKEN: fnl[str] = os.getenv('DISCORD_TOKEN')

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.getenv('SPOTIPY_CLIENT_ID'),
                                                           client_secret=os.getenv('SPOTIPY_CLIENT_SECRET')))


conn = sqlite3.connect('settings.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        guild_id INTEGER PRIMARY KEY,
        welcome_channel_id INTEGER
    )
''')


def set_welcome_channel(guild_id, channel_id):
    print(f'Setting welcome channel: guild_id={guild_id}, channel_id={channel_id}')
    try:
        c.execute('''
            INSERT OR REPLACE INTO settings (guild_id, welcome_channel_id)
            VALUES (?, ?)
        ''', (guild_id, channel_id))
        conn.commit()
        print('Welcome channel set successfully')
    except Exception as e:
        print(f'Error setting welcome channel: {e}')

def get_welcome_channel(guild_id):
    c.execute('''
        SELECT welcome_channel_id
        FROM settings
        WHERE guild_id = ?
    ''', (guild_id,))
    result = c.fetchone()
    return result[0] if result else None

def search_val_skin(skin_name):
    response = requests.get('https://valorant-api.com/v1/weapons/skins')
    data = response.json()

    matching_skins = []
    for skin in data['data']:
        if skin_name.lower() in skin['displayName'].lower():
            matching_skins.append(skin)

    return matching_skins


'''todo: implement player stats'''
'''
def get_val_player_stats(player_name):
    KEY = os.getenv('VALPY-KEY')
    val = valorant.Client(KEY, locale='en-US')
    player = val.get_user_by_name(player_name)

    matches = player.matchlist().history.fine(queueId='competitive')

    if not matches:
        return "No matches found"

    stats = ""
    for match in matches:
        match_details = match.get()
        for team in match_details.teams:
            if team.winner:
                stats += f"{team.teamId} Team's Ranks:\n"
                players = match_details.players.get_all(teamId=team.teamId)
                for player in players:
                    stats += f"\t{player.gameName} - {player.rank}\n"
    return stats
'''    

class WelcomeChannelMenu(menus.Menu):
    async def send_initial_message(self, ctx, channel):
        return await channel.send('React with 📝 to set the current channel as the welcome channel.')

    @menus.button('📝')
    async def on_set_welcome_channel(self, payload):
        set_welcome_channel(payload.guild_id, payload.channel_id)
        await self.message.edit(content=f'Successfully set the welcome channel to <#{payload.channel_id}>.')


def get_meme():
    response = requests.get('https://meme-api.com/gimme')
    json_data = json.loads(response.text)
    return json_data['url']



def get_random_usless_fact():
    response = requests.get('https://uselessfacts.jsph.pl/random.json?language=en')
    json_data = json.loads(response.text)
    return json_data['text']

def get_adop():
    try:
        params = {'api_key': os.getenv('NASA_API_KEY') }
        response = requests.get('https://api.nasa.gov/planetary/apod', params=params)
        response.raise_for_status()  # Raises a HTTPError if the response status is 4xx, 5xx

        json_data = response.json()
        return json_data['url']
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') 
        return 'an http error' # Python 3.6
    except requests.exceptions.RequestException as err:
        print(f'Error occurred: {err}')
        return 'An unknown error occurred.'  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}') 
        return 'An unknown error occurred.'


def get_nasa_images(query):
    try:
        params = {'q': query}
        response = requests.get('https://images-api.nasa.gov/search', params=params)
        response.raise_for_status()  # Raises a HTTPError if the response status is 4xx, 5xx

        json_data = response.json()
        items = json_data.get('collection', {}).get('items', [])
        urls = [item['links'][0]['href'] for item in items if 'links' in item and item['links'] and item['data'][0]['media_type'] == 'image']
        return '\n'.join(urls[:5])  # Return only the first 5 URLs
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') 
        return 'An HTTP error occurred.'
    except requests.exceptions.RequestException as err:
        print(f'Error occurred: {err}')
        return 'A request error occurred.'
    except Exception as err:
        print(f'Other error occurred: {err}') 
        return 'An unknown error occurred.'


bot = Bot(command_prefix=os.getenv('DISCORD_PREFIX'), intents=discord.Intents.all())


@bot.event
async def on_ready():
    print('Logged in as {0}!'.format(bot.user))
    await bot.change_presence(activity=discord.Game(name="!Help for commands"))


@bot.command()
async def clear(ctx, limit=100):
    await ctx.channel.purge(limit=limit)
    embed = discord.Embed(title=f'Deleted {limit} messages in this channel.')
    await ctx.send(embed=embed)


@bot.command(aliases=['hello', 'hi'])
async def greet(ctx):
    await ctx.send('Hello! nan thaan leo dasu! !Help use pani na ena panuven nu therinjukko!')


@bot.command()
async def meme(ctx):
    await ctx.send(get_meme())

@bot.command()
async def fact(ctx):
    await ctx.send(get_random_usless_fact())

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')


@bot.command()
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send("You need to be in a voice channel to use this command.")
    else:
        voice_channel = ctx.author.voice.channel
        vc = await voice_channel.connect()


@bot.command()
async def leave(ctx):
    if ctx.voice_client is None:
        await ctx.send("I am not in a voice channel.")
    else:
        await ctx.voice_client.disconnect()


@bot.command()
async def adop(ctx):
    await ctx.send(get_adop())


@bot.command()
async def nasa(ctx, *, query: str):
    await ctx.send(get_nasa_images(query))


@bot.command()
async def valskin(ctx, *, skin_name: str):
    skins = search_val_skin(skin_name)
    if skins:
        for skin in skins:
            embed = discord.Embed(title=skin['displayName'], color=0x00ff00)
            embed.set_image(url=skin['displayIcon'])  # Set the image
            await ctx.send(embed=embed)
    else:
        await ctx.send(f'No skin found for "{skin_name}".')
'''
@bot.command()
async def valstats(ctx, *, player_name: str):
    stats = get_val_player_stats(player_name)
    await ctx.send(stats)'''


@bot.command()
@commands.has_permissions(administrator=True)
async def welcome_channel_menu(ctx):
    await WelcomeChannelMenu().start(ctx)

@bot.event
async def on_member_join(member):
    channel_id = get_welcome_channel(member.guild.id)
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(f'Welcome to the server, {member.name}!')

@bot.event
async def on_member_remove(member):
    channel_id = get_welcome_channel(member.guild.id)
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(f'Goodbye, {member.name}!')


@bot.event
async def on_member_update(before, after):
    if before.nick != after.nick:
        print(f'{before.nick} changed their nickname to {after.nick}')


@bot.event
async def on_member_ban(guild, user):
    print(f'{user.name} was banned from {guild.name}')

@bot.event
async def on_member_unban(guild, user):
    print(f'{user.name} was unbanned from {guild.name}')

@bot.event
async def on_member_timeout(member):
    print(f'{member.name} timed out')

@bot.event
async def on_member_kick(member):
    print(f'{member.name} was kicked')



#TODO: Implement Spotify playlist support
'''
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

    await ctx.send(f'Playing {results["name"]} in {voice_channel}')'''

video_titles = {}
queues = {}

@bot.command()
async def play(ctx, *, track=None):
    if track is None:
        await ctx.send("Please specify a song to play.")
        return

    if ctx.author.voice is None:
        await ctx.send("You need to be in a voice channel to use this command.")
        return
    
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        vc = await voice_channel.connect()
    else:
        vc = ctx.voice_client

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
                video_title = info['entries'][0]['title']
                best_audio = max(info['entries'][0]['formats'], key=lambda format: format.get('abr') or 0)
                url = best_audio['url'] 
                print(url)
            else:
                await ctx.send(f'Error: No formats found for {track} on YouTube.')
                return
    except yt_dlp.utils.DownloadError:
        await ctx.send(f'Error: Could not find {track} on YouTube.')
        return

    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []
    queues[ctx.guild.id].append((url, video_title))   

    if not vc.is_playing():
        await start_playing(ctx, ctx.guild.id, vc, voice_channel)

    source = discord.FFmpegPCMAudio(executable="ffmpeg", source=url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
    vc.play(source)
    await ctx.send(f'Playing {video_title} in {voice_channel}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{video_title}"))
    video_titles[ctx.guild.id] = video_title

    while vc.is_playing():
        await asyncio.sleep(1)
    await bot.change_presence(activity=discord.Game(name="!Help for commands"))

async def start_playing(ctx, guild_id, vc, voice_channel):
    url, video_title = queues[guild_id].pop(0)
    source = discord.FFmpegPCMAudio(executable="ffmpeg", source=url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
    vc.play(source, after=lambda e: start_playing(ctx, guild_id, vc, voice_channel) if e is None else None)
    await ctx.send(f'Playing {video_title} in {voice_channel}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{video_title}"))


@bot.command()
async def pause(ctx):
    
    if ctx.voice_client is None:
        await ctx.send("I am not in a voice channel.")
    else:
        ctx.voice_client.pause()
        await ctx.send(f'Paused {video_titles.get(ctx.guild.id)} in {ctx.author.voice.channel}')
        await bot.change_presence(activity=discord.Game(name="!Help for commands"))

@bot.command()
async def resume(ctx):
    if ctx.voice_client is None:
        await ctx.send("I am not in a voice channel.")
    else:
        ctx.voice_client.resume()
        await ctx.send(f'Resumed {video_titles.get(ctx.guild.id)} in {ctx.author.voice.channel}')
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{video_titles.get(ctx.guild.id)}"))
@bot.command()
async def stop(ctx):
    if ctx.voice_client is None:
        await ctx.send("I am not in a voice channel.")
    else:
        ctx.voice_client.stop()
        await ctx.send(f'Stopped {video_titles.get(ctx.guild.id)} in {ctx.author.voice.channel}')
        await bot.change_presence(activity=discord.Game(name="!Help for commands"))


@bot.command()
async def Help(ctx):
    embed = discord.Embed(title='Help', description='List of available commands:', color=0x014e9d)
    embed.add_field(name='!hello / !hi', value='Greets the user', inline=False)
    embed.add_field(name='!meme', value='Sends a random meme', inline=False)
    embed.add_field(name='!ping', value='Returns the latency', inline=False)
    embed.add_field(name='!clear', value='Clears the chat', inline=False)
    embed.add_field(name='!play', value='Plays a song in the user\'s voice channel', inline=False)
    embed.add_field(name='!pause', value='Pauses the song', inline=False)
    embed.add_field(name='!resume', value='Resumes the song', inline=False)
    embed.add_field(name='!stop', value='Stops the song', inline=False)
    embed.add_field(name='!join', value='Joins the user\'s voice channel', inline=False)
    embed.add_field(name='!leave', value='Leaves the voice channel', inline=False)
    embed.add_field(name='!adop', value='Sends the Astronomy Picture of the Day', inline=False)
    embed.add_field(name='!nasa', value='Searches for images on NASA\'s API', inline=False)
    embed.add_field(name='!valskin', value='Searches for Valorant skins', inline=False) 
    embed.add_field(name='!fact', value='Sends a random useless fact', inline=False)
    embed.add_field(name='!welcome_channel_menu', value='Sets the welcome channel', inline=False)
    embed.add_field(name='!Help', value='Displays this message', inline=False)
    await ctx.send(embed=embed)


bot.run(TOKEN)