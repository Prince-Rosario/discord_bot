import asyncio
import re
from urllib.parse import urlparse
import discord
from discord import app_commands
import discord.opus 
import requests
import json
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

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


if not discord.opus.is_loaded():
    discord.opus.load_opus('/opt/homebrew/Cellar/opus/1.5.2/lib/libopus.0.dylib')

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

@client.event
async def on_ready():
    print('Logged in as {0}!'.format(client.user))
    await client.change_presence(activity=discord.Game(name="/help for commands"))
    await tree.sync()  # Sync the command tree with Discord

@tree.command(name="clear", description="Clears messages in the channel")
async def clear(interaction: discord.Interaction, limit: int = 100):
    await interaction.channel.purge(limit=limit)
    embed = discord.Embed(title=f'Deleted {limit} messages in this channel.')
    await interaction.response.send_message(embed=embed)

@tree.command(name="greet", description="Greets the user")
async def greet(interaction: discord.Interaction):
    await interaction.response.send_message('Hello! the name is Leo das! use /help to learn more!')

@tree.command(name="meme", description="Sends a random meme")
async def meme(interaction: discord.Interaction):
    await interaction.response.send_message(get_meme())

@tree.command(name="insult", description="Sends a random insult")
async def insult(interaction: discord.Interaction):
    await interaction.response.send_message(get_insult())

@tree.command(name="advice", description="Sends a random advice")
async def advice(interaction: discord.Interaction):
    await interaction.response.send_message(get_advice())

@tree.command(name="fact", description="Sends a random useless fact")
async def fact(interaction: discord.Interaction):
    await interaction.response.send_message(get_random_usless_fact())

@tree.command(name="ping", description="Returns the latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f'Pong! {round(client.latency * 1000)}ms')

@tree.command(name="join", description="Joins the user's voice channel")
async def join(interaction: discord.Interaction):
    if interaction.user.voice is None:
        await interaction.response.send_message("You need to be in a voice channel to use this command.")
    else:
        voice_channel = interaction.user.voice.channel
        await voice_channel.connect()
        await interaction.response.send_message(f"Joined {voice_channel}")

@tree.command(name="leave", description="Leaves the voice channel")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client is None:
        await interaction.response.send_message("I am not in a voice channel.")
    else:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Left the voice channel")

@tree.command(name="adop", description="Sends the Astronomy Picture of the Day")
async def adop(interaction: discord.Interaction):
    await interaction.response.send_message(get_adop())

@tree.command(name="nasa", description="Searches for images on NASA's API")
async def nasa(interaction: discord.Interaction, query: str):
    await interaction.response.send_message(get_nasa_images(query))

@tree.command(name="valskin", description="Searches for Valorant skins")
async def valskin(interaction: discord.Interaction, skin_name: str):
    skins = search_val_skin(skin_name)
    if skins:
        for skin in skins:
            embed = discord.Embed(title=skin['displayName'], color=0x00ff00)
            embed.set_image(url=skin['displayIcon'])  # Set the image
            await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f'No skin found for "{skin_name}".')



@tree.command(name="logchannel", description="Sets the log channel")
async def logchannel(interaction: discord.Interaction):
    menu = LogChannelMenu()
    await menu.start(interaction)

@tree.command(name="welcomechannel", description="Sets the welcome channel")
async def welcomechannel(interaction: discord.Interaction):
    menu = WelcomeChannelMenu()
    await menu.start(interaction)


@tree.command(name="help", description="List of available commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title='Help', description='List of available commands:', color=0x014e9d)
    embed.add_field(name='/greet', value='Greets the user', inline=False)
    embed.add_field(name='/meme', value='Sends a random meme', inline=False)
    embed.add_field(name='/ping', value='Returns the latency', inline=False)
    embed.add_field(name='/insult', value='Sends a random insult', inline=False)
    embed.add_field(name='/advice', value='Sends a random advice', inline=False)
    embed.add_field(name='/clear', value='Clears the chat', inline=False)
    embed.add_field(name='/join', value='Joins the user\'s voice channel', inline=False)
    embed.add_field(name='/leave', value='Leaves the voice channel', inline=False)
    embed.add_field(name='/adop', value='Sends the Astronomy Picture of the Day', inline=False)
    embed.add_field(name='/nasa', value='Searches for images on NASA\'s API', inline=False)
    embed.add_field(name='/valskin', value='Searches for Valorant skins', inline=False) 
    embed.add_field(name='/fact', value='Sends a random useless fact', inline=False)                  
    await interaction.response.send_message(embed=embed)

@client.event
async def on_member_join(member):
    channel_id = get_welcome_channel(member.guild.id)
    if channel_id:
        channel = client.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                title="Welcome to the server!",
                description=f"{member.name}, we're glad to have you here!",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=member.avatar.url)
            await channel.send(embed=embed)

@client.event
async def on_member_remove(member):
    channel_id = get_welcome_channel(member.guild.id)
    if channel_id:
        channel = client.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                title="Goodbye!",
                description=f"{member.name}, we're sad to see you go!",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=member.avatar.url)
            await channel.send(embed=embed)

@client.event
async def on_voice_state_update(member, before, after):
    timestamp = datetime.datetime.now()
    log_channel_id = get_log_channel(member.guild.id)
    if log_channel_id is not None:
        log_channel = client.get_channel(log_channel_id)
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

@client.event
async def on_member_update(before, after):
    if before.nick != after.nick:
        log_channel_id = get_log_channel(before.guild.id)
        if log_channel_id is not None:
            log_channel = client.get_channel(log_channel_id)
            if log_channel is not None:
                embed = Embed(title='Nickname Changed', description=f'{before.nick} changed their nickname to {after.nick}', colour=Colour.blue())
                await log_channel.send(embed=embed)

@client.event
async def on_member_ban(guild, user):
    log_channel_id = get_log_channel(guild.id)
    if log_channel_id is not None:
        log_channel = client.get_channel(log_channel_id)
        if log_channel is not None:
            embed = Embed(title='Member Banned', description=f'{user.name} was banned from {guild.name}', colour=Colour.blue())
            await log_channel.send(embed=embed)

@client.event
async def on_member_unban(guild, user):
    log_channel_id = get_log_channel(guild.id)
    if log_channel_id is not None:
        log_channel = client.get_channel(log_channel_id)
        if log_channel is not None:
            embed = Embed(title='Member Unbanned', description=f'{user.name} was unbanned from {guild.name}', colour=Colour.blue())
            await log_channel.send(embed=embed)

@client.event
async def on_member_timeout(member):
    log_channel_id = get_log_channel(member.guild.id)
    if log_channel_id is not None:
        log_channel = client.get_channel(log_channel_id)
        if log_channel is not None:
            embed = Embed(title='Member Timed Out', description=f'{member.name} timed out', colour=Colour.blue())
            await log_channel.send(embed=embed)

@client.event
async def on_member_kick(member):
    log_channel_id = get_log_channel(member.guild.id)
    if log_channel_id is not None:
        log_channel = client.get_channel(log_channel_id)
        if log_channel is not None:
            embed = Embed(title='Member Kicked', description=f'{member.name} was kicked', colour=Colour.blue())
            await log_channel.send(embed=embed)

#TODO: Implement Spotify playlist support

video_titles = {}
queues = {}

@tree.command(name="play", description="Plays a song in the user's voice channel")
async def play(interaction: discord.Interaction, track: str):
    if track is None:
        await interaction.response.send_message("Please specify a song to play.")
        return

    if interaction.user.voice is None:
        await interaction.response.send_message("You need to be in a voice channel to use this command.")
        return
    
    voice_channel = interaction.user.voice.channel
    if interaction.guild.voice_client is None:
        vc = await voice_channel.connect()
    else:
        vc = interaction.guild.voice_client

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
                await interaction.response.send_message(f'Error: No formats found for {track} on YouTube.')
                return
    except yt_dlp.utils.DownloadError:
        await interaction.response.send_message(f'Error: Could not find {track} on YouTube.')
        return

    if interaction.guild.id not in queues:
        queues[interaction.guild.id] = []
    queues[interaction.guild.id].append((url, video_title))   

    if not vc.is_playing():
        await start_playing(interaction, interaction.guild.id, vc, voice_channel)

currently_playing = {}

async def start_playing(interaction, guild_id, vc, voice_channel):
    if not queues[guild_id]:  # If the queue is empty, return
        return

    url, video_title = queues[guild_id].pop(0)
    source = discord.FFmpegPCMAudio(executable="ffmpeg", source=url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')

    currently_playing[guild_id] = video_title  # Store the currently playing song

    def after_callback(e):
        if e:  # If an error occurred, print it out
            print(f'Error in playback: {e}')
        coro = start_playing(interaction, guild_id, vc, voice_channel)  # Schedule the next song to play
        fut = asyncio.run_coroutine_threadsafe(coro, client.loop)
        try:
            fut.result()
        except:
            # an error was raised during the execution of the coroutine
            pass

    try:
        vc.play(source, after=after_callback)
        await interaction.response.send_message(f'Playing {video_title} in {voice_channel}')
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{video_title}"))
    except discord.opus.OpusNotLoaded:
        await interaction.response.send_message("Opus library is not loaded. Please ensure it is installed and properly configured.")

@tree.command(name="skip", description="Skips the current song")
async def skip(interaction: discord.Interaction):
    if interaction.guild.voice_client is None:
        await interaction.response.send_message("I am not in a voice channel.")
    else:
        current_song = currently_playing.get(interaction.guild.id, "None")  # Get the currently playing song
        interaction.guild.voice_client.stop()
        await interaction.response.send_message(f"Skipped {current_song} in {interaction.user.voice.channel}")
        await start_playing(interaction, interaction.guild.id, interaction.guild.voice_client, interaction.user.voice.channel)

@tree.command(name="queue", description="Displays the current queue")
async def queue(interaction: discord.Interaction):
    if not queues.get(interaction.guild.id):
        await interaction.response.send_message("The queue is empty.")
    else:
        queue_str = "\n".join([title for url, title in queues[interaction.guild.id]])
        await interaction.response.send_message(f"Current queue:\n{queue_str}")

@tree.command(name="pause", description="Pauses the song")
async def pause(interaction: discord.Interaction):
    if interaction.guild.voice_client is None:
        await interaction.response.send_message("I am not in a voice channel.")
    else:
        current_song = currently_playing.get(interaction.guild.id, "None")  # Get the currently playing song
        interaction.guild.voice_client.pause()
        await interaction.response.send_message(f"Paused {current_song} in {interaction.user.voice.channel}")

@tree.command(name="resume", description="Resumes the song")
async def resume(interaction: discord.Interaction):
    if interaction.guild.voice_client is None:
        await interaction.response.send_message("I am not in a voice channel.")
    else:
        current_song = currently_playing.get(interaction.guild.id, "None") # Get the currently playing song
        interaction.guild.voice_client.resume()
        await interaction.response.send_message(f"Resumed {current_song} in {interaction.user.voice.channel}")

@tree.command(name="stop", description="Stops the song")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client is None:
        await interaction.response.send_message("I am not in a voice channel.")
    else:
        current_song = currently_playing.get(interaction.guild.id, "None") # Get the currently playing song
        queues[interaction.guild.id] = [] # Clear the queue
        interaction.guild.voice_client.stop()
        await interaction.response.send_message(f"Stopped {current_song} in {interaction.user.voice.channel}")
        await client.change_presence(activity=discord.Game(name="/help for commands"))
client.run(TOKEN)
       