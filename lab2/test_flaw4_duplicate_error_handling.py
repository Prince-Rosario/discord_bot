import unittest
import re

class TestFlaw4DuplicateErrorHandling(unittest.TestCase):
    """Test suite for Flaw 4: Duplicate Error Handling anti-pattern in API functions"""
    
    def setUp(self):
        """Set up test fixtures by reading the bot.py file"""
        self.bot_file_path = 'bot.py'
        
        # Read the bot.py file
        with open(self.bot_file_path, 'r', encoding='utf-8') as f:
            self.bot_content = f.read()
            self.bot_lines = f.readlines()

    def test_api_functions_have_identical_error_structures(self):
        """Test that API functions have nearly identical error handling structures"""
        # Look for the specific 3-tier error handling pattern
        http_error_count = self.bot_content.count('HTTPError')
        request_exception_count = self.bot_content.count('RequestException')
        general_exception_count = self.bot_content.count('Exception')
        
        self.assertGreaterEqual(http_error_count, 2, 
                               f"Found {http_error_count} HTTPError handlers - multiple functions have identical error handling")
        self.assertGreaterEqual(request_exception_count, 2, 
                               f"Found {request_exception_count} RequestException handlers - indicates duplicate error handling")
        print(f"Found {http_error_count} HTTPError handlers and {request_exception_count} RequestException handlers")

    def test_get_adop_and_get_nasa_images_error_similarity(self):
        """Test that get_adop and get_nasa_images have nearly identical error handling"""
        # Check if both functions exist
        get_adop_found = 'def get_adop(' in self.bot_content
        get_nasa_found = 'def get_nasa_images(' in self.bot_content
        
        if not (get_adop_found and get_nasa_found):
            self.skipTest("Both get_adop and get_nasa_images functions required for this test")
        
        # Count similar error handling patterns
        error_patterns = [
            'requests.exceptions.HTTPError as http_err',
            'requests.exceptions.RequestException as err',
            'except Exception as err',
            'print(f\'HTTP error occurred:',
            'print(f\'Error occurred:',
            'print(f\'Other error occurred:'
        ]
        
        pattern_count = sum(1 for pattern in error_patterns if self.bot_content.count(pattern) >= 2)
        
        self.assertGreaterEqual(pattern_count, 4, 
                               f"Found {pattern_count} duplicated error patterns between API functions")
        print(f"Found {pattern_count} duplicated error patterns between get_adop and get_nasa_images")

    def test_repeated_exception_handling_patterns(self):
        """Test that exception handling patterns are repeated across multiple functions"""
        exception_patterns = {
            'http_error_pattern': 'except requests.exceptions.HTTPError',
            'request_exception_pattern': 'except requests.exceptions.RequestException',
            'general_exception_pattern': 'except Exception',
            'print_http_error': 'HTTP error occurred',
            'print_request_error': 'Error occurred',
            'print_other_error': 'Other error occurred',
            'return_error_message': 'error occurred',
            'raise_for_status': 'raise_for_status()'
        }
        
        duplicated_patterns = []
        for pattern_name, pattern in exception_patterns.items():
            count = self.bot_content.count(pattern)
            if count >= 2:  # Pattern appears multiple times
                duplicated_patterns.append(pattern_name)
        
        self.assertGreaterEqual(len(duplicated_patterns), 6, 
                               f"Found {len(duplicated_patterns)} duplicated exception patterns: {duplicated_patterns}")
        print(f"Found {len(duplicated_patterns)} duplicated exception patterns: {duplicated_patterns}")

if __name__ == '__main__':
    unittest.main(verbosity=2) 