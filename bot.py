import asyncio
import re
from urllib.parse import urlparse
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
import datetime
from discord import Embed, Colour

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

def add_log_channel_column():
    try:
        c.execute('''
            ALTER TABLE settings
            ADD COLUMN log_channel_id INTEGER
        ''')
        conn.commit()
        print('Log channel column added successfully')
    except Exception as e:
        print(f'Error adding log channel column: {e}')

add_log_channel_column()



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


def set_log_channel(guild_id, channel_id):
    print(f'Setting log channel: guild_id={guild_id}, channel_id={channel_id}')
    try:
        c.execute('''
            INSERT OR REPLACE INTO settings (guild_id, log_channel_id)
            VALUES (?, ?)
        ''', (guild_id, channel_id))
        conn.commit()
        print('Log channel set successfully')
    except Exception as e:
        print(f'Error setting log channel: {e}')

def get_log_channel(guild_id):
    c.execute('''
        SELECT log_channel_id
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


class LogChannelMenu(menus.Menu):
    async def send_initial_message(self, ctx, channel):
        return await channel.send('React with 📝 to set the current channel as the log channel.')

    @menus.button('📝')
    async def on_set_log_channel(self, payload):
        set_log_channel(payload.guild_id, payload.channel_id)
        await self.message.edit(content=f'Successfully set the log channel to <#{payload.channel_id}>.')








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

def get_insult():
    response = requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=json')
    if response.status_code == 200:
        data = response.json()
        return data['insult']
    else:
        return 'Error: Could not retrieve insult.'

def get_advice():
    response = requests.get('https://api.adviceslip.com/advice')
    json_data = json.loads(response.text)
    return json_data['slip']['advice']


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
    await ctx.send('Hello! the name is Leo das! use !Help to learn more!')

@bot.command()
@commands.has_permissions(administrator=True)
async def log_channel_menu(ctx):
    await LogChannelMenu().start(ctx)


@bot.command()
async def meme(ctx):
    await ctx.send(get_meme())

@bot.command()
async def insult(ctx):
    await ctx.send(get_insult())  

@bot.command()
async def advice(ctx):
    await ctx.send(get_advice())

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

@bot.command()
async def wish(ctx):
    await ctx.send('Thirumana Vazhthukkal HariHaran! Pathirikkai vaikadhadhuku nandri 🙏')

@bot.event
async def on_member_join(member):
    channel_id = get_welcome_channel(member.guild.id)
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                title="Welcome to the server!",
                description=f"{member.name}, we're glad to have you here!",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=member.avatar.url)
            await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    channel_id = get_welcome_channel(member.guild.id)
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                title="Goodbye!",
                description=f"{member.name}, we're sad to see you go!",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=member.avatar.url)
            await channel.send(embed=embed)


@bot.event
async def on_voice_state_update(member, before, after):
    timestamp = datetime.datetime.now()
    log_channel_id = get_log_channel(member.guild.id)
    if log_channel_id is not None:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel is not None:
            if after.channel is not None and after.channel.overwrites_for(member.guild.default_role).view_channel is False:
                return
            if before.channel is not None and before.channel.overwrites_for(member.guild.default_role).view_channel is False:
                return
            if before.channel == after.channel:  # Add this condition
                return  # Return if the voice channel hasn't changed
            join_embed = discord.Embed(color=discord.Colour.blue())
            left_embed = discord.Embed(color=discord.Colour.red())
            move_embed = discord.Embed(color=discord.Colour.gold())
            join_embed.set_author(name=member.name, icon_url=member.avatar.url)
            left_embed.set_author(name=member.name, icon_url=member.avatar.url)
            move_embed.set_author(name=member.name, icon_url=member.avatar.url)
            if before.channel is None and after.channel is not None:
                join_embed.title = 'Joined Voice Channel'
                join_embed.description = f'{member.name} joined voice channel {after.channel.name} at {format_time(timestamp)}'
                await log_channel.send(embed=join_embed)
            elif before.channel is not None and after.channel is None:
                left_embed.title = 'Left Voice Channel'
                left_embed.description = f'{member.name} left voice channel {before.channel.name} at {format_time(timestamp)}'
                await log_channel.send(embed=left_embed)
            elif before.channel is not None and after.channel is not None:
                move_embed.title = 'Moved Voice Channels'
                move_embed.description = f'{member.name} moved from voice channel {before.channel.name} to {after.channel.name} at {format_time(timestamp)}'
                await log_channel.send(embed=move_embed)

def format_time(timestamp):
    now = datetime.datetime.now()
    if timestamp.date() == now.date():
        return f'Today at <t:{int(timestamp.timestamp())}:t>'
    elif timestamp.date() == now.date() - datetime.timedelta(days=1):
        return f'Yesterday at <t:{int(timestamp.timestamp())}:t>'
    else:
        return f'<t:{int(timestamp.timestamp())}:F>'
@bot.event
async def on_member_update(before, after):
    if before.nick != after.nick:
        log_channel_id = get_log_channel(before.guild.id)
        if log_channel_id is not None:
            log_channel = bot.get_channel(log_channel_id)
            if log_channel is not None:
                embed = Embed(title='Nickname Changed', description=f'{before.nick} changed their nickname to {after.nick}', colour=Colour.blue())
                await log_channel.send(embed=embed)

@bot.event
async def on_member_ban(guild, user):
    log_channel_id = get_log_channel(guild.id)
    if log_channel_id is not None:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel is not None:
            embed = Embed(title='Member Banned', description=f'{user.name} was banned from {guild.name}', colour=Colour.blue())
            await log_channel.send(embed=embed)

@bot.event
async def on_member_unban(guild, user):
    log_channel_id = get_log_channel(guild.id)
    if log_channel_id is not None:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel is not None:
            embed = Embed(title='Member Unbanned', description=f'{user.name} was unbanned from {guild.name}', colour=Colour.blue())
            await log_channel.send(embed=embed)

@bot.event
async def on_member_timeout(member):
    log_channel_id = get_log_channel(member.guild.id)
    if log_channel_id is not None:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel is not None:
            embed = Embed(title='Member Timed Out', description=f'{member.name} timed out', colour=Colour.blue())
            await log_channel.send(embed=embed)

@bot.event
async def on_member_kick(member):
    log_channel_id = get_log_channel(member.guild.id)
    if log_channel_id is not None:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel is not None:
            embed = Embed(title='Member Kicked', description=f'{member.name} was kicked', colour=Colour.blue())
            await log_channel.send(embed=embed)


#TODO: Implement Spotify playlist support


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
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'geo_bypass': True,
        'nocheckcertificate': True
    }

    if urlparse(track).scheme and urlparse(track).netloc:
        ydl_opts['default_search'] = ''
        parsed_url = urlparse(track)
        track = f'{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}'
    else:
        ydl_opts['default_search'] = 'ytsearch'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f'{track}', download=False)
            
            if 'entries' in info and len(info['entries']) > 0:  # check if 'entries' is not empty
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

currently_playing = {}

async def start_playing(ctx, guild_id, vc, voice_channel):
    if not queues[guild_id]:  # If the queue is empty, return
        return

    url, video_title = queues[guild_id].pop(0)
    source = discord.FFmpegPCMAudio(executable="ffmpeg", source=url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')

    currently_playing[guild_id] = video_title  # Store the currently playing song

    def after_callback(e):
        if e:  # If an error occurred, print it out
            print(f'Error in playback: {e}')
        coro = start_playing(ctx, guild_id, vc, voice_channel)  # Schedule the next song to play
        fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
        try:
            fut.result()
        except:
            # an error was raised during the execution of the coroutine
            pass

    vc.play(source, after=after_callback)
    await ctx.send(f'Playing {video_title} in {voice_channel}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{video_title}"))


@bot.command()
async def skip(ctx):
    if ctx.voice_client is None:
        await ctx.send("I am not in a voice channel.")
    else:
        current_song = currently_playing.get(ctx.guild.id, "None")  # Get the currently playing song
        ctx.voice_client.stop()
        await ctx.send(f"Skipped {current_song} in {ctx.author.voice.channel}")
        await start_playing(ctx, ctx.guild.id, ctx.voice_client, ctx.author.voice.channel)

@bot.command()
async def queue(ctx):
    if not queues.get(ctx.guild.id):
        await ctx.send("The queue is empty.")
    else:
        queue_str = "\n".join([title for url, title in queues[ctx.guild.id]])
        await ctx.send(f"Current queue:\n{queue_str}")

@bot.command()
async def pause(ctx):
    if ctx.voice_client is None:
        await ctx.send("I am not in a voice channel.")
    else:
        current_song = currently_playing.get(ctx.guild.id, "None")  # Get the currently playing song
        ctx.voice_client.pause()
        await ctx.send(f"Paused {current_song} in {ctx.author.voice.channel}")

@bot.command()
async def resume(ctx):
    if ctx.voice_client is None:
        await ctx.send("I am not in a voice channel.")
    else:
        current_song = currently_playing.get(ctx.guild.id, "None")  # Get the currently playing song
        ctx.voice_client.resume()
        await ctx.send(f"Resumed {current_song} in {ctx.author.voice.channel}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client is None:
        await ctx.send("I am not in a voice channel.")
    else:
        current_song = currently_playing.get(ctx.guild.id, "None")  # Get the currently playing song
        queues[ctx.guild.id] = []  # Clear the queue
        ctx.voice_client.stop()
        await ctx.send(f"Stopped {current_song} in {ctx.author.voice.channel}")
        await bot.change_presence(activity=discord.Game(name="!Help for commands"))


@bot.command()
async def Help(ctx):
    embed = discord.Embed(title='Help', description='List of available commands:', color=0x014e9d)
    embed.add_field(name='!hello / !hi', value='Greets the user', inline=False)
    embed.add_field(name='!meme', value='Sends a random meme', inline=False)
    embed.add_field(name='!ping', value='Returns the latency', inline=False)
    embed.add_field(name='!insult', value='Sends a random insult', inline=False)
    embed.add_field(name='!advice', value='Sends a random advice', inline=False)
    embed.add_field(name='!clear', value='Clears the chat', inline=False)
    embed.add_field(name='!play', value='Plays a song in the user\'s voice channel', inline=False)
    embed.add_field(name='!pause', value='Pauses the song', inline=False)
    embed.add_field(name='!resume', value='Resumes the song', inline=False)
    embed.add_field(name='!skip', value='Skips the current song', inline=False)
    embed.add_field(name='!queue', value='Displays the current queue', inline=False)
    embed.add_field(name='!stop', value='Stops the song', inline=False)
    embed.add_field(name='!join', value='Joins the user\'s voice channel', inline=False)
    embed.add_field(name='!leave', value='Leaves the voice channel', inline=False)
    embed.add_field(name='!adop', value='Sends the Astronomy Picture of the Day', inline=False)
    embed.add_field(name='!nasa', value='Searches for images on NASA\'s API', inline=False)
    embed.add_field(name='!valskin', value='Searches for Valorant skins', inline=False) 
    embed.add_field(name='!fact', value='Sends a random useless fact', inline=False)
    embed.add_field(name='!welcome_channel_menu', value='Sets the welcome channel', inline=False)
    embed.add_field(name='!log_channel_menu', value='Sets the log channel', inline=False)
    await ctx.send(embed=embed)


bot.run(TOKEN)