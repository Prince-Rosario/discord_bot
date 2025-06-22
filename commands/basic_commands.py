"""
Basic Discord commands extracted from bot.py to fix God Object anti-pattern.
Contains simple utility commands like greet, ping, clear, etc.
"""

import discord
from discord import app_commands
import asyncio


class BasicCommands:
    """Handles basic Discord bot commands."""
    
    def __init__(self, tree: app_commands.CommandTree, client: discord.Client):
        self.tree = tree
        self.client = client
        self._register_commands()
    
    def _register_commands(self):
        """Register all basic commands."""
        
        @self.tree.command(name="clear", description="Clears messages in the channel")
        async def clear(interaction: discord.Interaction, limit: int = 100):
            # Defer the response to prevent timeout
            await interaction.response.defer(thinking=True)
            
            # Check if the user has manage messages permission
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.followup.send("You don't have permission to clear messages.")
                return
            
            deleted = await interaction.channel.purge(limit=limit)
            await interaction.followup.send(f"Cleared {len(deleted)} messages.")

        @self.tree.command(name="greet", description="Greets the user")
        async def greet(interaction: discord.Interaction):
            await interaction.response.send_message(f"Hello, {interaction.user.mention}!")

        @self.tree.command(name="ping", description="Returns the latency")
        async def ping(interaction: discord.Interaction):
            latency = round(self.client.latency * 1000)
            await interaction.response.send_message(f"Pong! Latency: {latency}ms")

        @self.tree.command(name="join", description="Joins the user's voice channel")
        async def join(interaction: discord.Interaction):
            if interaction.user.voice is None:
                await interaction.response.send_message("You need to be in a voice channel.")
                return
            
            voice_channel = interaction.user.voice.channel
            await voice_channel.connect()
            await interaction.response.send_message(f"Joined {voice_channel.name}")

        @self.tree.command(name="leave", description="Leaves the voice channel")
        async def leave(interaction: discord.Interaction):
            if interaction.guild.voice_client is None:
                await interaction.response.send_message("I am not in a voice channel.")
                return
            
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("Left the voice channel.")

        @self.tree.command(name="test", description="Simple test command to check if bot is working properly")
        async def test_command(interaction: discord.Interaction):
            try:
                await interaction.response.send_message("Bot is responding correctly to interactions!", ephemeral=True)
                print(f"Test command executed by {interaction.user.name}")
            except Exception as e:
                print(f"Error in test command: {e}")

        @self.tree.command(name="help", description="List of available commands")
        async def help_command(interaction: discord.Interaction):
            embed = discord.Embed(title="Bot Commands", color=0x00ff00)
            embed.add_field(name="/greet", value="Greets the user", inline=False)
            embed.add_field(name="/ping", value="Returns the bot's latency", inline=False)
            embed.add_field(name="/clear [limit]", value="Clears messages in the channel", inline=False)
            embed.add_field(name="/join", value="Joins your voice channel", inline=False)
            embed.add_field(name="/leave", value="Leaves the voice channel", inline=False)
            embed.add_field(name="/play [track]", value="Plays a song in your voice channel", inline=False)
            embed.add_field(name="/skip", value="Skips the current song", inline=False)
            embed.add_field(name="/queue", value="Displays the current queue", inline=False)
            embed.add_field(name="/pause", value="Pauses the current song", inline=False)
            embed.add_field(name="/resume", value="Resumes the current song", inline=False)
            embed.add_field(name="/stop", value="Stops the current song and clears the queue", inline=False)
            embed.add_field(name="/meme", value="Sends a random meme", inline=False)
            embed.add_field(name="/insult", value="Sends a random insult", inline=False)
            embed.add_field(name="/advice", value="Sends random advice", inline=False)
            embed.add_field(name="/fact", value="Sends a random useless fact", inline=False)
            embed.add_field(name="/adop", value="Sends NASA's Astronomy Picture of the Day", inline=False)
            embed.add_field(name="/nasa [query]", value="Searches NASA's image database", inline=False)
            embed.add_field(name="/valskin [name]", value="Searches for Valorant weapon skins", inline=False)
            embed.add_field(name="/logchannel", value="Sets the current channel as the log channel", inline=False)
            embed.add_field(name="/welcomechannel", value="Sets the current channel as the welcome channel", inline=False)
            
            await interaction.response.send_message(embed=embed) 