"""
Domain objects for guild settings to fix Data Clumps anti-pattern.
Groups related data (guild_id, channel_id) into cohesive objects.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class GuildChannelPair:
    """Represents a guild and channel combination to eliminate data clumps."""
    guild_id: int
    channel_id: int
    
    def __post_init__(self):
        """Validate the guild and channel IDs."""
        if not isinstance(self.guild_id, int) or self.guild_id <= 0:
            raise ValueError("guild_id must be a positive integer")
        if not isinstance(self.channel_id, int) or self.channel_id <= 0:
            raise ValueError("channel_id must be a positive integer")


@dataclass 
class GuildSettings:
    """Encapsulates all settings for a guild to eliminate primitive obsession."""
    guild_id: int
    welcome_channel_id: Optional[int] = None
    log_channel_id: Optional[int] = None
    
    def __post_init__(self):
        """Validate the guild ID."""
        if not isinstance(self.guild_id, int) or self.guild_id <= 0:
            raise ValueError("guild_id must be a positive integer")
    
    @property
    def welcome_channel(self) -> Optional[GuildChannelPair]:
        """Get welcome channel as a domain object."""
        if self.welcome_channel_id:
            return GuildChannelPair(self.guild_id, self.welcome_channel_id)
        return None
    
    @property
    def log_channel(self) -> Optional[GuildChannelPair]:
        """Get log channel as a domain object."""
        if self.log_channel_id:
            return GuildChannelPair(self.guild_id, self.log_channel_id)
        return None
    
    def set_welcome_channel(self, channel_id: int) -> None:
        """Set welcome channel with validation."""
        if not isinstance(channel_id, int) or channel_id <= 0:
            raise ValueError("channel_id must be a positive integer")
        self.welcome_channel_id = channel_id
    
    def set_log_channel(self, channel_id: int) -> None:
        """Set log channel with validation."""
        if not isinstance(channel_id, int) or channel_id <= 0:
            raise ValueError("channel_id must be a positive integer")
        self.log_channel_id = channel_id 