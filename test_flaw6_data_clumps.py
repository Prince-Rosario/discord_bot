import unittest
import re

class TestFlaw6DataClumps(unittest.TestCase):
    """Test suite for Flaw 6: Data Clumps anti-pattern"""
    
    def setUp(self):
        """Set up test fixtures by reading the bot.py file"""
        self.bot_file_path = 'bot.py'
        
        # Read the bot.py file
        with open(self.bot_file_path, 'r', encoding='utf-8') as f:
            self.bot_content = f.read()
            self.bot_lines = f.readlines()

    def test_database_functions_share_same_parameter_pattern(self):
        """Test that database functions all share the same guild_id, channel_id parameter pattern"""
        # Count functions that use both guild_id and channel_id
        functions_with_both = 0
        for func in ['set_welcome_channel', 'set_log_channel', 'get_welcome_channel', 'get_log_channel']:
            if func in self.bot_content and 'guild_id' in self.bot_content and 'channel_id' in self.bot_content:
                functions_with_both += 1
        
        self.assertGreaterEqual(functions_with_both, 2, 
                               f"Found {functions_with_both} database functions with guild_id,channel_id clump - should be grouped into a class")
        print(f"Found {functions_with_both} database functions using guild_id,channel_id parameter clump")

    def test_member_guild_id_pattern_repetition(self):
        """Test that member.guild.id pattern is repeated across multiple functions"""
        member_guild_pattern_count = self.bot_content.count('member.guild.id')
        guild_id_access_count = self.bot_content.count('.guild.id')
        
        self.assertGreaterEqual(member_guild_pattern_count + guild_id_access_count, 4, 
                               f"Found {member_guild_pattern_count + guild_id_access_count} instances of guild.id pattern - indicates data clump")
        print(f"Found {member_guild_pattern_count} member.guild.id patterns and {guild_id_access_count} .guild.id patterns")

    def test_absence_of_guild_channel_wrapper_class(self):
        """Test that there's no wrapper class for guild-channel combinations"""
        # Look for wrapper class definitions
        wrapper_class_patterns = [
            r'class GuildChannel\b',
            r'class ChannelSettings\b',
            r'class GuildSettings\b',
            r'class ServerChannel\b',
            r'class GuildChannelPair\b'
        ]
        
        found_wrapper_classes = []
        for pattern in wrapper_class_patterns:
            if re.search(pattern, self.bot_content):
                found_wrapper_classes.append(pattern)
        
        self.assertEqual(len(found_wrapper_classes), 0, 
                        f"Found wrapper classes: {found_wrapper_classes} - but data clumps still exist")
        print("No wrapper classes found for guild-channel combinations - data clump should be refactored into a class")

if __name__ == '__main__':
    unittest.main(verbosity=2) 