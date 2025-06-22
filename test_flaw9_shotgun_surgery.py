import unittest
import re

class TestFlaw9ShotgunSurgery(unittest.TestCase):
    """Test suite for Flaw 9: Shotgun Surgery anti-pattern"""
    
    def setUp(self):
        """Set up test fixtures by reading the bot.py file"""
        self.bot_file_path = 'bot.py'
        
        # Read the bot.py file
        with open(self.bot_file_path, 'r', encoding='utf-8') as f:
            self.bot_content = f.read()
            self.bot_lines = f.readlines()

    def test_discord_interaction_handling_scattered(self):
        """Test that Discord interaction handling is scattered across functions"""
        interaction_functions = self.bot_content.count('interaction')
        tree_commands = self.bot_content.count('@tree.command')
        
        self.assertGreaterEqual(tree_commands, 15, 
                               f"Found {tree_commands} scattered command handlers - indicates shotgun surgery")
        print(f"Found {tree_commands} @tree.command handlers and {interaction_functions} interaction references")

    def test_guild_operations_scattered_across_codebase(self):
        """Test that guild operations are scattered across the codebase"""
        guild_operations = [
            'guild_id',
            '.guild.',
            'member.guild',
            'interaction.guild',
            'payload.guild_id'
        ]
        
        total_guild_ops = sum(self.bot_content.count(op) for op in guild_operations)
        
        self.assertGreaterEqual(total_guild_ops, 20, 
                               f"Found {total_guild_ops} guild operations scattered across codebase")
        print(f"Found {total_guild_ops} guild operations scattered across the codebase")

    def test_lack_of_centralized_abstractions(self):
        """Test that there's a lack of centralized abstractions leading to shotgun surgery"""
        # Look for centralized abstraction classes
        abstraction_patterns = [
            r'class CommandHandler\b',
            r'class GuildManager\b',
            r'class InteractionHandler\b',
            r'class DatabaseManager\b',
            r'class ApiClient\b',
            r'class MusicManager\b',
            r'class ChannelManager\b'
        ]
        
        found_abstractions = []
        for pattern in abstraction_patterns:
            if re.search(pattern, self.bot_content):
                found_abstractions.append(pattern)
        
        self.assertEqual(len(found_abstractions), 0, 
                        f"Found abstractions: {found_abstractions} - but functionality is still scattered")
        print("No centralized abstractions found - all functionality scattered across individual functions")

if __name__ == '__main__':
    unittest.main(verbosity=2) 