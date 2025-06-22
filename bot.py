"""
Main Discord bot entry point.
Refactored to fix God Object anti-pattern by extracting functionality into separate modules.
"""

import discord
from discord import app_commands
import discord.opus 
from dotenv import load_dotenv
import os
from typing import Final as fnl
import platform

# Import our extracted modules
from database_manager import DatabaseManager
from api_manager import APIManager
from commands import BasicCommands, APICommands, SettingsCommands
from guild_settings import GuildChannelPair

# Discord client setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Load opus for voice functionality
if platform.system() == 'Linux':
    discord.opus.load_opus('/usr/lib/x86_64-linux-gnu/libopus.so.0')
else:
    discord.opus.load_opus('/opt/homebrew/Cellar/opus/1.5.2/lib/libopus.0.dylib')    

# Load environment variables
load_dotenv()
TOKEN: fnl[str] = os.getenv('DISCORD_TOKEN')
NASA_API_KEY: fnl[str] = os.getenv('NASA_API_KEY', 'DEMO_KEY')

# Initialize managers
db_manager = DatabaseManager()
api_manager = APIManager(NASA_API_KEY)

# Initialize command modules
basic_commands = BasicCommands(tree, client)
api_commands = APICommands(tree, api_manager)
settings_commands = SettingsCommands(tree, db_manager)


@client.event
async def on_ready():
    """Bot ready event."""
    print(f'Logged in as {client.user}!')
    await client.change_presence(activity=discord.Game(name="/help for commands"))
    
    # Sync commands globally
    try:
        synced = await tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(f'Failed to sync commands: {e}')


@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Global command error handler."""
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f'Command is on cooldown. Try again in {error.retry_after:.2f} seconds.', ephemeral=True)
    elif isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
    else:
        await interaction.response.send_message('An error occurred while executing the command.', ephemeral=True)
        print(f'Command error: {error}')


@client.event
async def on_member_join(member):
    """Handle member join events."""
    welcome_channel_id = db_manager.get_channel(member.guild.id, 'welcome_channel_id')
    if welcome_channel_id:
        welcome_channel = client.get_channel(welcome_channel_id)
        if welcome_channel:
            embed = discord.Embed(title="Welcome!", description=f"Welcome to the server, {member.mention}!", color=0x00ff00)
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            await welcome_channel.send(embed=embed)


@client.event
async def on_member_remove(member):
    """Handle member leave events."""
    welcome_channel_id = db_manager.get_channel(member.guild.id, 'welcome_channel_id')
    if welcome_channel_id:
        welcome_channel = client.get_channel(welcome_channel_id)
        if welcome_channel:
            embed = discord.Embed(title="Goodbye!", description=f"{member.display_name} has left the server.", color=0xff0000)
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            await welcome_channel.send(embed=embed)


def is_channel_hidden(channel, guild):
    """Check if a voice channel is hidden from @everyone."""
    return channel.overwrites_for(guild.default_role).view_channel is False


def create_voice_embed(member, embed_type):
    """Create embed for voice state changes."""
    colors = {'join': 0x00ff00, 'leave': 0xff0000, 'move': 0x0099ff}
    titles = {'join': 'Voice Channel Join', 'leave': 'Voice Channel Leave', 'move': 'Voice Channel Move'}
    
    embed = discord.Embed(title=titles[embed_type], color=colors[embed_type])
    embed.set_author(name=member.display_name, icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
    return embed


async def handle_voice_join(member, after_channel, log_channel, timestamp):
    """Handle voice channel join."""
    embed = create_voice_embed(member, 'join')
    embed.add_field(name="Joined", value=after_channel.name, inline=False)
    embed.timestamp = timestamp
    await log_channel.send(embed=embed)


async def handle_voice_leave(member, before_channel, log_channel, timestamp):
    """Handle voice channel leave."""
    embed = create_voice_embed(member, 'leave')
    embed.add_field(name="Left", value=before_channel.name, inline=False)
    embed.timestamp = timestamp
    await log_channel.send(embed=embed)


async def handle_voice_move(member, before_channel, after_channel, log_channel, timestamp):
    """Handle voice channel move."""
    embed = create_voice_embed(member, 'move')
    embed.add_field(name="From", value=before_channel.name, inline=True)
    embed.add_field(name="To", value=after_channel.name, inline=True)
    embed.timestamp = timestamp
    await log_channel.send(embed=embed)


@client.event
async def on_voice_state_update(member, before, after):
    """Handle voice state updates with improved conditional logic."""
    # Early returns to reduce complexity
    if before.channel == after.channel:
        return
    
    log_channel_id = db_manager.get_channel(member.guild.id, 'log_channel_id')
    if not log_channel_id:
        return
    
    log_channel = client.get_channel(log_channel_id)
    if not log_channel:
        return
    
    # Skip hidden channels
    if after.channel and is_channel_hidden(after.channel, member.guild):
        return
    if before.channel and is_channel_hidden(before.channel, member.guild):
        return
    
    timestamp = discord.utils.utcnow()
    
    # Handle different voice state changes
    if before.channel is None and after.channel is not None:
        await handle_voice_join(member, after.channel, log_channel, timestamp)
    elif before.channel is not None and after.channel is None:
        await handle_voice_leave(member, before.channel, log_channel, timestamp)
    elif before.channel is not None and after.channel is not None:
        await handle_voice_move(member, before.channel, after.channel, log_channel, timestamp)


# Music commands - simplified versions (complex music functionality can be added later)
@tree.command(name="play", description="Plays a song in the user's voice channel")
async def play(interaction: discord.Interaction, track: str):
    """Simplified play command - placeholder for future music functionality."""
    await interaction.response.send_message(f"🎵 Music functionality for '{track}' will be implemented in future versions.")


@tree.command(name="skip", description="Skips the current song")
async def skip(interaction: discord.Interaction):
    """Skip current song."""
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("⏭️ Skipped current track.")
    else:
        await interaction.response.send_message("❌ No song is currently playing.")


@tree.command(name="queue", description="Displays the current queue")
async def queue(interaction: discord.Interaction):
    """Display music queue."""
    embed = discord.Embed(title="🎵 Music Queue", color=0x00ff00)
    embed.add_field(name="Status", value="Music queue functionality will be implemented in future versions.", inline=False)
    await interaction.response.send_message(embed=embed)


@tree.command(name="pause", description="Pauses the song")
async def pause(interaction: discord.Interaction):
    """Pause current song."""
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.pause()
        await interaction.response.send_message("⏸️ Paused the current song.")
    else:
        await interaction.response.send_message("❌ No song is currently playing.")


@tree.command(name="resume", description="Resumes the song")
async def resume(interaction: discord.Interaction):
    """Resume paused song."""
    if interaction.guild.voice_client and interaction.guild.voice_client.is_paused():
        interaction.guild.voice_client.resume()
        await interaction.response.send_message("▶️ Resumed the current song.")
    else:
        await interaction.response.send_message("❌ No song is currently paused.")


@tree.command(name="stop", description="Stops the song")
async def stop(interaction: discord.Interaction):
    """Stop music and clear queue."""
    if interaction.guild.voice_client:
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("⏹️ Stopped the music.")
    else:
        await interaction.response.send_message("❌ No music is currently playing.")


if __name__ == "__main__":
    client.run(TOKEN)
       