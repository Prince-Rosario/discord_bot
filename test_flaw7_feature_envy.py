import unittest
import re

class TestFlaw7FeatureEnvy(unittest.TestCase):
    """Test suite for Flaw 7: Feature Envy anti-pattern"""
    
    def setUp(self):
        """Set up test fixtures by reading the bot.py file"""
        self.bot_file_path = 'bot.py'
        
        # Read the bot.py file
        with open(self.bot_file_path, 'r', encoding='utf-8') as f:
            self.bot_content = f.read()
            self.bot_lines = f.readlines()

    def test_interaction_object_property_access_frequency(self):
        """Test that functions frequently access interaction object properties"""
        interaction_count = self.bot_content.count('interaction.')
        
        self.assertGreaterEqual(interaction_count, 50, 
                               f"Found {interaction_count} interaction property accesses - indicates feature envy")
        print(f"Found {interaction_count} interaction property accesses - indicates feature envy")

    def test_violation_of_law_of_demeter(self):
        """Test that functions violate the Law of Demeter with chained property access"""
        # Look for chained property access patterns
        chained_patterns = [
            'interaction.user.voice',
            'member.guild.id',
            'response.json()',
            'data[\'data\']',
            'skin[\'displayName\']',
            'item[\'links\'][0]',
            '.guild.id',
            '.user.id',
            '.channel.id'
        ]
        
        violation_count = 0
        for pattern in chained_patterns:
            violation_count += self.bot_content.count(pattern)
        
        self.assertGreaterEqual(violation_count, 15, 
                               f"Found {violation_count} Law of Demeter violations - indicates feature envy")
        print(f"Found {violation_count} chained property accesses violating Law of Demeter")

    def test_lack_of_domain_objects_for_external_data(self):
        """Test that there are no domain objects for external data structures"""
        # Look for domain object classes for external data
        domain_class_patterns = [
            r'class ValorantSkin\b',
            r'class NasaImage\b',
            r'class MemeData\b',
            r'class ApiResponse\b',
            r'class DiscordUser\b',
            r'class VoiceState\b',
            r'class GuildMember\b'
        ]
        
        found_domain_classes = []
        for pattern in domain_class_patterns:
            if re.search(pattern, self.bot_content):
                found_domain_classes.append(pattern)
        
        self.assertEqual(len(found_domain_classes), 0, 
                        f"Found domain classes: {found_domain_classes} - but external data is still accessed directly")
        print("No domain objects found for external data - all external data accessed directly (feature envy)")

if __name__ == '__main__':
    unittest.main(verbosity=2) 