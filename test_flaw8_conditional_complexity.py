import unittest
import re

class TestFlaw8ConditionalComplexity(unittest.TestCase):
    """Test suite for Flaw 8: Conditional Complexity anti-pattern"""
    
    def setUp(self):
        """Set up test fixtures by reading the bot.py file"""
        self.bot_file_path = 'bot.py'
        
        # Read the bot.py file
        with open(self.bot_file_path, 'r', encoding='utf-8') as f:
            self.bot_content = f.read()
            self.bot_lines = f.readlines()

    def test_on_voice_state_update_has_deep_nesting(self):
        """Test that on_voice_state_update function has deeply nested if statements"""
        # Check if function exists
        if 'async def on_voice_state_update(' not in self.bot_content:
            self.skipTest("on_voice_state_update function not found")
        
        # Count nested if statements in the function (rough estimate)
        nested_if_patterns = ['    if ', '        if ', '            if ']
        nested_count = sum(self.bot_content.count(pattern) for pattern in nested_if_patterns)
        
        self.assertGreaterEqual(nested_count, 3, 
                               f"Found {nested_count} nested if statements - indicates deep nesting complexity")
        print(f"Found {nested_count} nested if statements in on_voice_state_update")

    def test_functions_with_excessive_boolean_operators(self):
        """Test that functions have excessive boolean operators"""
        and_count = self.bot_content.count(' and ')
        or_count = self.bot_content.count(' or ')
        
        total_boolean_ops = and_count + or_count
        self.assertGreater(total_boolean_ops, 30, 
                          f"Found {total_boolean_ops} boolean operators - indicates conditional complexity")
        print(f"Found {and_count} 'and' operators and {or_count} 'or' operators (total: {total_boolean_ops})")

    def test_cyclomatic_complexity_indicators(self):
        """Test for high cyclomatic complexity indicators"""
        # Count complexity indicators
        if_count = len(re.findall(r'\bif\b', self.bot_content))
        elif_count = len(re.findall(r'\belif\b', self.bot_content))
        try_count = len(re.findall(r'\btry\b', self.bot_content))
        except_count = len(re.findall(r'\bexcept\b', self.bot_content))
        for_count = len(re.findall(r'\bfor\b', self.bot_content))
        while_count = len(re.findall(r'\bwhile\b', self.bot_content))
        
        # Calculate approximate total complexity
        total_complexity = if_count + elif_count + try_count + except_count + for_count + while_count
        
        self.assertGreater(total_complexity, 100, 
                          f"Found {total_complexity} complexity indicators - indicates high cyclomatic complexity")
        print(f"Complexity indicators: {if_count} ifs, {elif_count} elifs, {try_count} tries, {except_count} excepts")
        print(f"Total complexity indicators: {total_complexity}")

if __name__ == '__main__':
    unittest.main(verbosity=2) 