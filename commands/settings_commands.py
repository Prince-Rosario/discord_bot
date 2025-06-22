"""
Settings-related Discord commands extracted from bot.py to fix God Object anti-pattern.
Contains commands for configuring guild settings like welcome channels, log channels, etc.
"""

import discord
from discord import app_commands
from database_manager import DatabaseManager
from guild_settings import GuildChannelPair


class SettingsCommands:
    """Handles settings-related Discord bot commands."""
    
    def __init__(self, tree: app_commands.CommandTree, db_manager: DatabaseManager):
        self.tree = tree
        self.db_manager = db_manager
        self._register_commands()
    
    def _register_commands(self):
        """Register all settings-related commands."""
        
        @self.tree.command(name="welcomechannel", description="Sets the current channel as the welcome channel")
        async def welcomechannel(interaction: discord.Interaction):
            guild_channel = GuildChannelPair(interaction.guild.id, interaction.channel.id)
            
            success = self.db_manager.set_guild_setting(
                guild_channel.guild_id, 
                'welcome_channel_id', 
                guild_channel.channel_id
            )
            
            if success:
                await interaction.response.send_message(
                    f"Welcome channel set to {interaction.channel.mention}"
                )
            else:
                await interaction.response.send_message(
                    "Failed to set welcome channel. Please try again."
                )

        @self.tree.command(name="logchannel", description="Sets the current channel as the log channel")
        async def logchannel(interaction: discord.Interaction):
            guild_channel = GuildChannelPair(interaction.guild.id, interaction.channel.id)
            
            success = self.db_manager.set_guild_setting(
                guild_channel.guild_id, 
                'log_channel_id', 
                guild_channel.channel_id
            )
            
            if success:
                await interaction.response.send_message(
                    f"Log channel set to {interaction.channel.mention}"
                )
            else:
                await interaction.response.send_message(
                    "Failed to set log channel. Please try again."
                ) 