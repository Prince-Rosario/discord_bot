import unittest
import re

class TestFlaw2LongMethod(unittest.TestCase):
    """Test suite for Flaw 2: Long Method anti-pattern in bot.py"""
    
    def setUp(self):
        """Set up test fixtures by reading the bot.py file"""
        self.bot_file_path = 'bot.py'
        
        # Read the bot.py file
        with open(self.bot_file_path, 'r', encoding='utf-8') as f:
            self.bot_content = f.read()
        
        with open(self.bot_file_path, 'r', encoding='utf-8') as f:
            self.bot_lines = f.readlines()

    def test_play_function_exists_and_is_long(self):
        """Test that the play function exists and is excessively long"""
        # Find play function in the file
        play_function_found = False
        play_start = -1
        
        for i, line in enumerate(self.bot_lines):
            if 'async def play(' in line and 'playalt' not in line and 'playdirect' not in line:
                play_function_found = True
                play_start = i
                break
        
        self.assertTrue(play_function_found, "play function should exist in bot.py")
        
        # Count lines in play function (rough estimate)
        if play_start != -1:
            # Count lines until next function or end of file
            play_lines = 0
            for i in range(play_start + 1, len(self.bot_lines)):
                line = self.bot_lines[i]
                if (line.startswith('def ') or line.startswith('async def ') or line.startswith('@')) and not line.strip().startswith('#'):
                    break
                if line.strip():  # Count non-empty lines
                    play_lines += 1
            
            self.assertGreater(play_lines, 80, 
                              f"play function has approximately {play_lines} lines - indicates Long Method anti-pattern")
            print(f"play function has approximately {play_lines} lines - indicates Long Method anti-pattern")

    def test_play_function_has_multiple_responsibilities(self):
        """Test that the play function handles too many different responsibilities"""
        # Extract play function content roughly
        play_content = ""
        in_play_function = False
        
        for line in self.bot_lines:
            if 'async def play(' in line and 'playalt' not in line and 'playdirect' not in line:
                in_play_function = True
                play_content += line
            elif in_play_function:
                if (line.startswith('def ') or line.startswith('async def ') or line.startswith('@')) and not line.strip().startswith('#'):
                    break
                play_content += line
        
        if not play_content:
            self.skipTest("play function not found")
        
        responsibilities = {
            'Input Validation': ['if track is None', 'if interaction.user.voice is None'],
            'Voice Channel Management': ['voice_channel.connect', 'voice_client'],
            'Cookie Management': ['cookies_file_path', 'create_fresh_cookies'],
            'YouTube-DL Configuration': ['ydl_opts', 'YoutubeDL'],
            'Error Handling': ['try:', 'except'],
            'Queue Management': ['queues[', 'currently_playing['],
            'Audio Processing': ['FFmpegPCMAudio', 'play(']
        }
        
        found_responsibilities = []
        for responsibility, patterns in responsibilities.items():
            if any(pattern in play_content for pattern in patterns):
                found_responsibilities.append(responsibility)
        
        self.assertGreaterEqual(len(found_responsibilities), 5, 
                               f"play function handles {len(found_responsibilities)} responsibilities - violates SRP")
        print(f"play function handles {len(found_responsibilities)} responsibilities: {found_responsibilities}")

    def test_cyclomatic_complexity_indicators(self):
        """Test that the codebase has high cyclomatic complexity indicators"""
        # Count complexity indicators throughout the file
        if_count = len(re.findall(r'\bif\b', self.bot_content))
        elif_count = len(re.findall(r'\belif\b', self.bot_content))
        try_count = len(re.findall(r'\btry\b', self.bot_content))
        except_count = len(re.findall(r'\bexcept\b', self.bot_content))
        for_count = len(re.findall(r'\bfor\b', self.bot_content))
        while_count = len(re.findall(r'\bwhile\b', self.bot_content))
        
        # Calculate approximate total complexity
        total_complexity = if_count + elif_count + try_count + except_count + for_count + while_count
        
        self.assertGreater(total_complexity, 100, 
                          f"Codebase has {total_complexity} complexity indicators - indicates high overall complexity")
        print(f"Codebase complexity indicators: {if_count} ifs, {try_count} tries, {except_count} excepts")
        print(f"Total complexity indicators: {total_complexity}")

if __name__ == '__main__':
    unittest.main(verbosity=2) 