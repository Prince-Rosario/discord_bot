import unittest
import os
import re

class TestFlaw1GodObject(unittest.TestCase):
    """Test suite for Flaw 1: God Object anti-pattern in bot.py"""
    
    def setUp(self):
        """Set up test fixtures by reading the bot.py file"""
        self.bot_file_path = 'bot.py'
        
        # Read the bot.py file
        with open(self.bot_file_path, 'r', encoding='utf-8') as f:
            self.bot_content = f.read()
        
        with open(self.bot_file_path, 'r', encoding='utf-8') as f:
            self.bot_lines = f.readlines()
    
    def test_file_length_indicates_god_object(self):
        """Test that bot.py is excessively long, indicating a God Object"""
        # Count non-empty, non-comment lines
        line_count = 0
        for line in self.bot_lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                line_count += 1
        
        self.assertGreater(line_count, 500, 
                          f"File has {line_count} lines of actual code - indicates God Object anti-pattern")
        print(f"bot.py has {len(self.bot_lines)} total lines with {line_count} lines of actual code - indicates God Object anti-pattern")

    def test_multiple_import_categories_present(self):
        """Test that the file imports from many different domains - sign of God Object"""
        import_categories = {
            'discord': ['discord', 'discord.ext'],
            'database': ['sqlite3'],
            'web': ['requests', 'aiohttp'],
            'audio': ['yt_dlp', 'youtube_dl'],
            'system': ['os', 'asyncio', 'datetime'],
            'data': ['json', 'random']
        }
        
        found_categories = []
        for category, imports in import_categories.items():
            if any(imp in self.bot_content for imp in imports):
                found_categories.append(category)
        
        self.assertGreaterEqual(len(found_categories), 5, 
                               f"File imports from {len(found_categories)} different domains - indicates God Object")
        print(f"File imports from {len(found_categories)} different domains: {found_categories} - indicates God Object")

    def test_multiple_responsibility_domains(self):
        """Test that the file handles multiple distinct responsibility domains"""
        responsibilities = {
            'Database Operations': ['CREATE TABLE', 'INSERT', 'SELECT', 'c.execute'],
            'API Integration': ['requests.get', 'response.json', 'api'],
            'Discord Events': ['@client.event', 'on_ready', 'on_member'],
            'Music Playback': ['yt_dlp', 'voice_client', 'play', 'queue'],
            'Command Handling': ['@tree.command', 'interaction.response'],
            'Error Handling': ['try:', 'except', 'Exception']
        }
        
        found_responsibilities = []
        for responsibility, patterns in responsibilities.items():
            if any(pattern in self.bot_content for pattern in patterns):
                found_responsibilities.append(responsibility)
        
        self.assertGreaterEqual(len(found_responsibilities), 5, 
                               f"File handles {len(found_responsibilities)} distinct responsibilities - violates SRP")
        print(f"File handles {len(found_responsibilities)} responsibilities: {found_responsibilities}")

if __name__ == '__main__':
    unittest.main(verbosity=2)