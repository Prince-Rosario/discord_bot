import unittest
import re

class TestFlaw5PrimitiveObsession(unittest.TestCase):
    """Test suite for Flaw 5: Primitive Obsession anti-pattern"""
    
    def setUp(self):
        """Set up test fixtures by reading the bot.py file"""
        self.bot_file_path = 'bot.py'
        
        # Read the bot.py file
        with open(self.bot_file_path, 'r', encoding='utf-8') as f:
            self.bot_content = f.read()
            self.bot_lines = f.readlines()

    def test_guild_id_used_as_primitive_in_multiple_functions(self):
        """Test that guild_id is used as primitive integer across multiple functions"""
        guild_id_count = self.bot_content.count('guild_id')
        
        self.assertGreaterEqual(guild_id_count, 10, 
                               f"Found {guild_id_count} uses of guild_id as primitive - should use Guild domain object")
        print(f"Found {guild_id_count} uses of guild_id as primitive across multiple functions")

    def test_channel_id_used_as_primitive_in_multiple_functions(self):
        """Test that channel_id is used as primitive integer across multiple functions"""
        channel_id_count = self.bot_content.count('channel_id')
        
        self.assertGreaterEqual(channel_id_count, 8, 
                               f"Found {channel_id_count} uses of channel_id as primitive - should use Channel domain object")
        print(f"Found {channel_id_count} uses of channel_id as primitive across multiple functions")

    def test_lack_of_domain_object_classes(self):
        """Test that there are no domain object classes defined"""
        # Look for domain class definitions
        domain_class_patterns = [
            r'class Guild\b',
            r'class Channel\b', 
            r'class GuildSettings\b',
            r'class DiscordGuild\b',
            r'class VoiceChannel\b',
            r'class TextChannel\b',
            r'class GuildId\b',
            r'class ChannelId\b'
        ]
        
        found_domain_classes = []
        for pattern in domain_class_patterns:
            if re.search(pattern, self.bot_content):
                found_domain_classes.append(pattern)
        
        self.assertEqual(len(found_domain_classes), 0, 
                        f"Found domain classes: {found_domain_classes} - but primitives are still used everywhere")
        print("No domain classes found - all domain concepts are represented as primitives")

if __name__ == '__main__':
    unittest.main(verbosity=2) 