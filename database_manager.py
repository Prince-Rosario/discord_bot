"""
Database manager to fix Duplicate Code anti-pattern.
Extracts common database operations into reusable methods.
"""

import sqlite3
from typing import Optional
from guild_settings import GuildSettings


class DatabaseManager:
    """Manages database operations for guild settings."""
    
    def __init__(self, db_path: str = 'settings.db'):
        """Initialize database connection and create tables."""
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self) -> None:
        """Create the settings table if it doesn't exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                guild_id INTEGER PRIMARY KEY,
                welcome_channel_id INTEGER,
                log_channel_id INTEGER
            )
        ''')
        self.conn.commit()
    
    def _execute_with_error_handling(self, query: str, params: tuple, operation_name: str) -> bool:
        """Execute database query with consistent error handling.
        
        This method eliminates duplicate error handling code across database operations.
        """
        try:
            print(f'{operation_name}: guild_id={params[0] if params else "N/A"}')
            self.cursor.execute(query, params)
            self.conn.commit()
            print(f'{operation_name} completed successfully')
            return True
        except Exception as e:
            print(f'Error in {operation_name}: {e}')
            return False
    
    def set_channel(self, guild_id: int, channel_id: int, channel_type: str) -> bool:
        """Generic method to set any channel type, eliminating code duplication."""
        if channel_type not in ['welcome_channel_id', 'log_channel_id']:
            raise ValueError(f"Invalid channel type: {channel_type}")
        
        query = f'''
            INSERT OR REPLACE INTO settings (guild_id, {channel_type})
            VALUES (?, ?)
        '''
        operation_name = f"Setting {channel_type.replace('_id', '').replace('_', ' ')}"
        return self._execute_with_error_handling(query, (guild_id, channel_id), operation_name)
    
    def get_channel(self, guild_id: int, channel_type: str) -> Optional[int]:
        """Generic method to get any channel type, eliminating code duplication."""
        if channel_type not in ['welcome_channel_id', 'log_channel_id']:
            raise ValueError(f"Invalid channel type: {channel_type}")
        
        query = f'''
            SELECT {channel_type}
            FROM settings
            WHERE guild_id = ?
        '''
        try:
            self.cursor.execute(query, (guild_id,))
            result = self.cursor.fetchone()
            return result[0] if result and result[0] else None
        except Exception as e:
            print(f'Error getting {channel_type}: {e}')
            return None
    
    def get_guild_settings(self, guild_id: int) -> GuildSettings:
        """Get complete guild settings as a domain object."""
        welcome_channel_id = self.get_channel(guild_id, 'welcome_channel_id')
        log_channel_id = self.get_channel(guild_id, 'log_channel_id')
        
        return GuildSettings(
            guild_id=guild_id,
            welcome_channel_id=welcome_channel_id,
            log_channel_id=log_channel_id
        )
    
    def save_guild_settings(self, settings: GuildSettings) -> bool:
        """Save complete guild settings using domain object."""
        success = True
        if settings.welcome_channel_id:
            success &= self.set_channel(settings.guild_id, settings.welcome_channel_id, 'welcome_channel_id')
        if settings.log_channel_id:
            success &= self.set_channel(settings.guild_id, settings.log_channel_id, 'log_channel_id')
        return success
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close() 