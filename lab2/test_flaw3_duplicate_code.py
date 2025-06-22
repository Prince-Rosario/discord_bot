import unittest
import re

class TestFlaw3DuplicateCode(unittest.TestCase):
    """Test suite for Flaw 3: Duplicate Code anti-pattern in database operations"""
    
    def setUp(self):
        """Set up test fixtures by reading the bot.py file"""
        self.bot_file_path = 'bot.py'
        
        # Read the bot.py file
        with open(self.bot_file_path, 'r', encoding='utf-8') as f:
            self.bot_content = f.read()
            self.bot_lines = f.readlines()

    def test_set_channel_functions_are_nearly_identical(self):
        """Test that set_welcome_channel and set_log_channel are duplicated code"""
        # Check if both functions exist
        set_welcome_found = 'def set_welcome_channel(' in self.bot_content
        set_log_found = 'def set_log_channel(' in self.bot_content
        
        self.assertTrue(set_welcome_found and set_log_found, 
                       "Both set functions should exist and be nearly identical")
        
        # Count similar patterns between the functions
        similar_patterns = [
            'INSERT OR REPLACE INTO settings',
            'VALUES (?, ?)',
            'conn.commit()',
            'except Exception as e:',
            'print(f\'Setting',
            'successfully\')'
        ]
        
        pattern_count = sum(1 for pattern in similar_patterns if self.bot_content.count(pattern) >= 2)
        
        self.assertGreaterEqual(pattern_count, 4, 
                               f"Found {pattern_count} duplicated patterns between set functions - indicates code duplication")
        print(f"Found {pattern_count} duplicated patterns between set_welcome_channel and set_log_channel")

    def test_get_channel_functions_are_nearly_identical(self):
        """Test that get_welcome_channel and get_log_channel are duplicated code"""
        # Check if both functions exist
        get_welcome_found = 'def get_welcome_channel(' in self.bot_content
        get_log_found = 'def get_log_channel(' in self.bot_content
        
        self.assertTrue(get_welcome_found and get_log_found, 
                       "Both get functions should exist and be nearly identical")
        
        # Count similar patterns between the functions
        similar_patterns = [
            'SELECT',
            'FROM settings',
            'WHERE guild_id = ?',
            'c.fetchone()',
            'return result[0] if result else None'
        ]
        
        pattern_count = sum(1 for pattern in similar_patterns if self.bot_content.count(pattern) >= 2)
        
        self.assertGreaterEqual(pattern_count, 4, 
                               f"Found {pattern_count} duplicated patterns between get functions - indicates code duplication")
        print(f"Found {pattern_count} duplicated patterns between get_welcome_channel and get_log_channel")

    def test_database_operation_patterns_are_duplicated(self):
        """Test that database operation patterns are repeated across functions"""
        # Common database patterns to look for
        patterns = {
            'insert_or_replace': 'INSERT OR REPLACE INTO',
            'commit_pattern': 'conn.commit()',
            'execute_pattern': 'c.execute(',
            'try_except': 'try:',
            'print_setting': 'print(f\'Setting',
            'print_success': 'successfully\')',
            'where_guild_id': 'WHERE guild_id = ?',
            'values_placeholder': 'VALUES (?, ?)'
        }
        
        duplicated_patterns = []
        for pattern_name, pattern in patterns.items():
            count = self.bot_content.count(pattern)
            if count >= 2:  # Pattern appears multiple times
                duplicated_patterns.append(pattern_name)
        
        self.assertGreaterEqual(len(duplicated_patterns), 5, 
                               f"Found {len(duplicated_patterns)} duplicated patterns: {duplicated_patterns} - indicates code duplication")
        print(f"Found {len(duplicated_patterns)} duplicated patterns: {duplicated_patterns} - indicates code duplication")

if __name__ == '__main__':
    unittest.main(verbosity=2) 