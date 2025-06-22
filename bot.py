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


# import youtube_dl
import yt_dlp

from discord.ext import commands 
from discord.ext import menus
import sqlite3
import datetime
from discord import Embed, Colour
import platform

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


if platform.system() == 'Linux':
    discord.opus.load_opus('/usr/lib/x86_64-linux-gnu/libopus.so.0')
else:
    discord.opus.load_opus('/opt/homebrew/Cellar/opus/1.5.2/lib/libopus.0.dylib')    

load_dotenv()
TOKEN: fnl[str] = os.getenv('DISCORD_TOKEN')



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
    
    # Sync commands globally
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Error handler for application commands."""
    print(f"Command error: {error}")
    
    # Check if we've already responded to this interaction
    if interaction.response.is_done():
        try:
            await interaction.followup.send(f"An error occurred: {error}", ephemeral=True)
        except Exception as e:
            print(f"Error sending followup: {e}")
    else:
        try:
            await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)
        except Exception as e:
            print(f"Error sending response: {e}")

@tree.command(name="clear", description="Clears messages in the channel")
async def clear(interaction: discord.Interaction, limit: int = 100):
    # Defer the response to prevent timeout
    await interaction.response.defer()

    # Purge messages
    deleted = await interaction.channel.purge(limit=limit)

    # Send a follow-up message with the result
    embed = discord.Embed(title=f'Deleted {len(deleted)} messages in this channel.')
    await interaction.followup.send(embed=embed)

@tree.command(name="greet", description="Greets the user")
async def greet(interaction: discord.Interaction):
    try:
        await interaction.response.send_message('Hello! My name is Leo das! Use /help to learn more!', ephemeral=True)
        print(f"Greeted user {interaction.user.name}")
    except Exception as e:
        print(f"Error in greet command: {e}")
        # Try followup if response failed
        try:
            if interaction.response.is_done():
                await interaction.followup.send("Hello there!", ephemeral=True)
        except Exception as follow_e:
            print(f"Follow-up also failed: {follow_e}")

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
        # Send the first response
        first_skin = skins.pop(0)
        embed = discord.Embed(title=first_skin['displayName'], color=0x00ff00)
        embed.set_image(url=first_skin['displayIcon'])
        await interaction.response.send_message(embed=embed)

        # Send follow-up messages for the remaining skins
        for skin in skins:
            embed = discord.Embed(title=skin['displayName'], color=0x00ff00)
            embed.set_image(url=skin['displayIcon'])
            await interaction.followup.send(embed=embed)
    else:
        await interaction.response.send_message(f'No skin found for "{skin_name}".')



@tree.command(name="logchannel", description="Sets the log channel")
async def logchannel(interaction: discord.Interaction):
    await interaction.response.send_message(
        'React with 📝 to set the current channel as the log channel.'
    )

    # Fetch the message to add a reaction
    message = await interaction.original_response()
    await message.add_reaction('📝')

    def check(reaction, user):
        return user == interaction.user and str(reaction.emoji) == '📝'

    try:
        reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
        set_log_channel(interaction.guild.id, interaction.channel.id)
        await interaction.followup.send(f'Successfully set the log channel to <#{interaction.channel.id}>.')
    except asyncio.TimeoutError:
        await interaction.followup.send('You did not react in time.')

@tree.command(name="welcomechannel", description="Sets the welcome channel")
async def welcomechannel(interaction: discord.Interaction):
    menu = WelcomeChannelMenu()
    await menu.start(interaction)


@tree.command(name="help", description="List of available commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title='Help', description='List of available commands:', color=0x014e9d)
    
    # General commands
    embed.add_field(name='General', value=
                    '`/greet` - Greets the user\n'
                    '`/meme` - Sends a random meme\n'
                    '`/ping` - Returns the latency\n'
                    '`/insult` - Sends a random insult\n'
                    '`/advice` - Sends a random advice\n'
                    '`/clear` - Clears the chat\n'
                    '`/fact` - Sends a random useless fact', inline=False)
    
    # Music commands
    embed.add_field(name='Music', value=
                    '`/play [track]` - Plays a song from YouTube\n'
                    '`/playalt [track]` - Tries alternative sources (SoundCloud)\n'
                    '`/playdirect [track]` - Direct MP3 streaming (when others fail)\n'
                    '`/queue` - Shows the current queue\n'
                    '`/skip` - Skips the current song\n'
                    '`/pause` - Pauses playback\n'
                    '`/resume` - Resumes playback\n'
                    '`/stop` - Stops playback\n'
                    '`/join` - Joins your voice channel\n'
                    '`/leave` - Leaves the voice channel', inline=False)
    
    # Other features
    embed.add_field(name='Other', value=
                    '`/adop` - Sends the Astronomy Picture of the Day\n'
                    '`/nasa [query]` - Searches for images on NASA\'s API\n'
                    '`/valskin [skin_name]` - Searches for Valorant skins\n'
                    '`/test` - Tests if the bot is working properly', inline=False)
                     
    await interaction.response.send_message(embed=embed, ephemeral=True)

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

def create_fresh_cookies(cookie_path):
    """
    Try to create fresh cookies using yt-dlp's built-in functionality
    """
    try:
        print(f"Attempting to create fresh cookies at: {cookie_path}")
        # Use yt-dlp to generate cookies
        temp_opts = {
            'quiet': False,
            'verbose': True,
            'cookiefile': cookie_path,
            'cookiesfrombrowser': ('chrome',),  # Try to extract from Chrome
            'skip_download': True
        }
        
        with yt_dlp.YoutubeDL(temp_opts) as ydl:
            # Just try to access a simple video to generate cookies
            ydl.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ", download=False)
            print("Successfully created fresh cookies")
            return True
    except Exception as e:
        print(f"Error creating fresh cookies: {e}")
        return False

@tree.command(name="play", description="Plays a song in the user's voice channel")
async def play(interaction: discord.Interaction, track: str):
    try:
        if track is None:
            await interaction.response.send_message("Please specify a song to play.")
            return

        if interaction.user.voice is None:
            await interaction.response.send_message("You need to be in a voice channel to use this command.")
            return

        # Defer the response to allow more time for processing
        await interaction.response.defer(thinking=True)

        voice_channel = interaction.user.voice.channel
        if interaction.guild.voice_client is None:
            vc = await voice_channel.connect()
        else:
            vc = interaction.guild.voice_client

        ###Path to your cookies file
        cookies_file_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')
        print(cookies_file_path)
        
        # Try to create fresh cookies if they don't work
        cookie_regenerated = False
        
        # First attempt with normal options
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': False,  # Set to False to see detailed output
            'geo_bypass': True,
            'nocheckcertificate': True,
            'cookiefile': cookies_file_path,  # Add the cookies file here
            'verbose': True,
            'extractor_retries': 5,
            'ignoreerrors': True,
            'skip_download': True,
            'source_address': '0.0.0.0',  # Bind to all interfaces
            'socket_timeout': 30,
            'extract_flat': True,
            'no_warnings': False,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/'
        }

        if urlparse(track).scheme and urlparse(track).netloc:
            ydl_opts['default_search'] = ''
            parsed_url = urlparse(track)
            track = f'{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}'
        else:
            ydl_opts['default_search'] = 'ytsearch'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f'{track}', download=False)
                
                if 'entries' in info and len(info['entries']) > 0:  # Check if 'entries' is not empty
                    video_title = info['entries'][0]['title']
                    best_audio = max(info['entries'][0]['formats'], key=lambda format: format.get('abr') or 0)
                    url = best_audio['url'] 
                    print(url)
                elif 'formats' in info:  # Direct URL
                    video_title = info.get('title', 'Unknown Title')
                    best_audio = max(info['formats'], key=lambda format: format.get('abr') or 0)
                    url = best_audio['url']
                    print(url)
                else:
                    await interaction.followup.send(f'Error: No formats found for {track} on YouTube.')
                    return
            except Exception as e:
                print(f"First extraction method failed: {e}")
                
                # Try regenerating cookies if not already tried
                if not cookie_regenerated and "Sign in to confirm you're not a bot" in str(e):
                    await interaction.followup.send("YouTube detected automation. Trying to refresh cookies...")
                    if create_fresh_cookies(cookies_file_path):
                        cookie_regenerated = True
                        # Try again with fresh cookies
                        try:
                            with yt_dlp.YoutubeDL(ydl_opts) as retry_ydl:
                                retry_info = retry_ydl.extract_info(f'{track}', download=False)
                                
                                if 'entries' in retry_info and len(retry_info['entries']) > 0:
                                    video_title = retry_info['entries'][0]['title']
                                    best_audio = max(retry_info['entries'][0]['formats'], key=lambda format: format.get('abr') or 0)
                                    url = best_audio['url']
                                    print(f"Retry successful with fresh cookies: {url}")
                                    
                                    if interaction.guild.id not in queues:
                                        queues[interaction.guild.id] = []
                                    queues[interaction.guild.id].append((url, video_title))
                                    
                                    if not vc.is_playing():
                                        await start_playing(interaction, interaction.guild.id, vc, voice_channel)
                                    return
                                elif 'formats' in retry_info:
                                    video_title = retry_info.get('title', 'Unknown Title')
                                    best_audio = max(retry_info['formats'], key=lambda format: format.get('abr') or 0)
                                    url = best_audio['url']
                                    print(f"Retry successful with fresh cookies: {url}")
                                    
                                    if interaction.guild.id not in queues:
                                        queues[interaction.guild.id] = []
                                    queues[interaction.guild.id].append((url, video_title))
                                    
                                    if not vc.is_playing():
                                        await start_playing(interaction, interaction.guild.id, vc, voice_channel)
                                    return
                        except Exception as retry_e:
                            print(f"Retry with fresh cookies failed: {retry_e}")
                
                # If cookie regeneration failed or wasn't triggered, try alternative approach
                alt_ydl_opts = {
                    'format': 'bestaudio/best',
                    'quiet': False,
                    'no_warnings': False,
                    'nocheckcertificate': True,
                    'extract_flat': 'in_playlist',
                    'default_search': 'ytsearch' if not (urlparse(track).scheme and urlparse(track).netloc) else '',
                    'skip_download': True
                }
                
                try:
                    with yt_dlp.YoutubeDL(alt_ydl_opts) as alt_ydl:
                        alt_info = alt_ydl.extract_info(f'{track}', download=False)
                        
                        if 'entries' in alt_info and len(alt_info['entries']) > 0:
                            video_title = alt_info['entries'][0]['title']
                            # Try a different service as fallback
                            search_term = alt_info['entries'][0]['title']
                            await interaction.followup.send(f"YouTube extraction failed. Trying alternative source for: {search_term}")
                            
                            # Use invidious as alternative
                            invidious_opts = {
                                'format': 'bestaudio/best',
                                'quiet': False,
                                'no_warnings': False,
                                'extract_flat': 'in_playlist',
                                'default_search': 'ytsearch',
                                'skip_download': True,
                                'extractor_args': {'youtubedl': {'skip': ['youtube']}}
                            }
                            
                            with yt_dlp.YoutubeDL(invidious_opts) as inv_ydl:
                                inv_info = inv_ydl.extract_info(f"ytsearch:{search_term}", download=False)
                                if 'entries' in inv_info and len(inv_info['entries']) > 0:
                                    video_title = inv_info['entries'][0]['title']
                                    best_audio = max(inv_info['entries'][0]['formats'], key=lambda format: format.get('abr') or 0)
                                    url = best_audio['url']
                                    print(f"Alternative extraction successful: {url}")
                                else:
                                    await interaction.followup.send(f'Error: Could not find alternative source for {track}.')
                                    return
                        else:
                            await interaction.followup.send(f'Error: No results found for {track}.')
                            return
                except Exception as alt_e:
                    await interaction.followup.send(f"Failed to play track: {alt_e}")
                    print(f"Alternative extraction failed: {alt_e}")
                    return

        if interaction.guild.id not in queues:
            queues[interaction.guild.id] = []
        queues[interaction.guild.id].append((url, video_title))   

        if not vc.is_playing():
            await start_playing(interaction, interaction.guild.id, vc, voice_channel)

    except yt_dlp.utils.DownloadError as e:
        await interaction.followup.send(f"Download error: {e}")
        print(f"Download error: {e}")
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}")
        print(f"Error in play command: {e}")

currently_playing = {}

async def start_playing(interaction, guild_id, vc, voice_channel):
    if not queues[guild_id]:  # If the queue is empty, return
        await client.change_presence(activity=discord.Game(name="/help for commands"))  # Reset status
        return

    url, video_title = queues[guild_id].pop(0)
    
    # Special handling for SoundCloud HLS streams
    before_options = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
    
    # Add protocol whitelist and other options for HLS streams
    if 'playlist.m3u8' in url or '.m3u8' in url:
        before_options += ' -protocol_whitelist file,http,https,tcp,tls,crypto -allowed_extensions ALL'
    
    source = discord.FFmpegPCMAudio(
        executable="ffmpeg", 
        source=url, 
        before_options=before_options
    )

    currently_playing[guild_id] = video_title  # Store the currently playing song

    def after_callback(e):
        if e:  # If an error occurred, print it out
            print(f'Error in playback: {e}')
        coro = start_playing(interaction, guild_id, vc, voice_channel)  # Schedule the next song to play
        fut = asyncio.run_coroutine_threadsafe(coro, client.loop)
        try:
            fut.result()
        except Exception as ex:
            print(f"Error scheduling next song: {ex}")
            # An error was raised during the execution of the coroutine
            pass

    try:
        vc.play(source, after=after_callback)
        await interaction.followup.send(f'Playing {video_title} in {voice_channel}')
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{video_title}"))
    except discord.opus.OpusNotLoaded:
        await interaction.followup.send("Opus library is not loaded. Please ensure it is installed and properly configured.")
    except Exception as e:
        await interaction.followup.send(f"Error playing audio: {e}")
        print(f"Error playing audio: {e}")

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

@tree.command(name="playalt", description="Play a song using alternative sources when YouTube doesn't work")
async def playalt(interaction: discord.Interaction, track: str):
    try:
        if track is None:
            await interaction.response.send_message("Please specify a song to play.")
            return

        if interaction.user.voice is None:
            await interaction.response.send_message("You need to be in a voice channel to use this command.")
            return

        # Defer the response to allow more time for processing
        await interaction.response.defer(thinking=True)

        voice_channel = interaction.user.voice.channel
        if interaction.guild.voice_client is None:
            vc = await voice_channel.connect()
        else:
            vc = interaction.guild.voice_client
        
        # Use SoundCloud or other alternative sources
        alt_ydl_opts = {
            'format': 'bestaudio/best[protocol^=http]',  # Prefer HTTP protocols over HLS
            'quiet': False,
            'no_warnings': False,
            'nocheckcertificate': True,
            'skip_download': True,
            'default_search': 'scsearch',  # Use SoundCloud search
            'extractor_args': {'youtubedl': {'skip': ['youtube']}},  # Skip YouTube
            'prefer_insecure': True,
            'legacy_server_connect': True,  # Try legacy connection method
        }
        
        await interaction.followup.send(f"Looking for '{track}' on alternate sources...")
        
        try:
            with yt_dlp.YoutubeDL(alt_ydl_opts) as alt_ydl:
                info = alt_ydl.extract_info(f"scsearch:{track}", download=False)
                
                if 'entries' in info and len(info['entries']) > 0:  # Check if 'entries' is not empty
                    entry = info['entries'][0]
                    video_title = entry['title']
                    
                    # Try to get a direct progressive HTTP URL if available
                    formats = entry.get('formats', [])
                    best_format = None
                    
                    # Try to find a non-HLS format first (direct MP3/HTTP stream)
                    for fmt in formats:
                        protocol = fmt.get('protocol', '')
                        if protocol != 'hls' and protocol != 'm3u8_native' and protocol != 'm3u8':
                            if best_format is None or fmt.get('abr', 0) > best_format.get('abr', 0):
                                best_format = fmt
                    
                    # If no direct stream found, use the best one available
                    if best_format is None and formats:
                        best_format = max(formats, key=lambda fmt: fmt.get('abr', 0))
                    
                    if best_format:
                        url = best_format['url']
                        print(f"Found on alternate source: {url}")
                        print(f"Format details: {best_format.get('protocol', 'unknown')}, {best_format.get('format_id', 'unknown')}")
                        
                        if interaction.guild.id not in queues:
                            queues[interaction.guild.id] = []
                        queues[interaction.guild.id].append((url, video_title))
                        
                        if not vc.is_playing():
                            await start_playing(interaction, interaction.guild.id, vc, voice_channel)
                    else:
                        await interaction.followup.send(f'Error: Could not find a playable format for "{track}".')
                else:
                    await interaction.followup.send(f'Error: No results found for "{track}" on alternate sources.')
        except Exception as alt_e:
            await interaction.followup.send(f"Alternative source failed: {alt_e}")
            print(f"Error in alternate source search: {alt_e}")
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}")
        print(f"Error in playalt command: {e}")

@tree.command(name="test", description="Simple test command to check if bot is working properly")
async def test_command(interaction: discord.Interaction):
    try:
        await interaction.response.send_message("Bot is responding correctly to interactions!", ephemeral=True)
        print(f"Test command executed by {interaction.user.name}")
    except Exception as e:
        print(f"Error in test command: {e}")

@tree.command(name="playdirect", description="Play music using direct MP3 sources (for when other methods fail)")
async def playdirect(interaction: discord.Interaction, track: str):
    try:
        if track is None:
            await interaction.response.send_message("Please specify a song to play.")
            return

        if interaction.user.voice is None:
            await interaction.response.send_message("You need to be in a voice channel to use this command.")
            return

        # Defer the response to allow more time for processing
        await interaction.response.defer(thinking=True)

        voice_channel = interaction.user.voice.channel
        if interaction.guild.voice_client is None:
            vc = await voice_channel.connect()
        else:
            vc = interaction.guild.voice_client
            
        # Try searching using different extraction methods
        await interaction.followup.send(f"Searching for a direct stream for '{track}'...")
        
        # Try using a more compatible source with direct MP3 links
        try:
            # Try using Jamendo (free music)
            jamendo_opts = {
                'format': 'bestaudio/best',
                'quiet': False,
                'default_search': 'jamendosearch', 
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(jamendo_opts) as jdl:
                info = jdl.extract_info(f"jamendosearch5:{track}", download=False)
                
                if info and 'entries' in info and len(info['entries']) > 0:
                    entry = info['entries'][0]
                    video_title = entry.get('title', 'Unknown Track')
                    url = entry.get('url')
                    
                    if url:
                        print(f"Found on Jamendo: {url}")
                        
                        if interaction.guild.id not in queues:
                            queues[interaction.guild.id] = []
                        queues[interaction.guild.id].append((url, video_title))
                        
                        if not vc.is_playing():
                            await start_playing(interaction, interaction.guild.id, vc, voice_channel)
                        return
        except Exception as e:
            print(f"Jamendo search failed: {e}")

        # If Jamendo fails, try to directly play an MP3 stream as a fallback
        encoded_query = track.replace(' ', '+')
        # This is a basic example - replace with an actual MP3 stream service if needed
        direct_mp3_url = f"https://mp3.fastupload.co/data/1621191941/{encoded_query}.mp3"
        
        # Add to queue
        video_title = f"{track} (direct stream)"
        if interaction.guild.id not in queues:
            queues[interaction.guild.id] = []
        queues[interaction.guild.id].append((direct_mp3_url, video_title))
        
        if not vc.is_playing():
            await start_playing(interaction, interaction.guild.id, vc, voice_channel)
            
    except Exception as e:
        await interaction.followup.send(f"Direct playback failed: {e}")
        print(f"Error in playdirect command: {e}")

if __name__ == "__main__":
    client.run(TOKEN)
       