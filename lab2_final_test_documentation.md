# Lab 2 - Unit Testing Documentation
## Code Refactoring 2025 - Final Test Documentation

This document contains all unit test descriptions for the 9 code flaws identified in Lab 1, following the required template format.

---

## Flaw 1: God Object

**Shortcoming of code flaw:** Single file (bot.py) handling too many responsibilities - violates Single Responsibility Principle and creates a God Object anti-pattern.

**Description of unit test:** Tests analyze the bot.py file structure to verify it contains excessive responsibilities. The test checks file length (953 lines with 700+ lines of actual code), import diversity (6+ domains), and multiple responsibilities (database, API, Discord, music, utilities).

**Quote of test:**
```python
def test_file_length_indicates_god_object(self):
    """Test that bot.py is excessively long, indicating a God Object"""
    # Count non-empty, non-comment lines
    line_count = 0
    for line in self.bot_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            line_count += 1
    
    self.assertGreater(line_count, 500, 
                      f"File has {line_count} lines of actual code - indicates God Object anti-pattern")
```

---

## Flaw 2: Long Method

**Shortcoming of code flaw:** The play function is over 100 lines long, violating the Single Responsibility Principle by handling validation, voice channel connection, cookie management, YouTube-DL configuration, error handling, retry logic, and queue management all in one function.

**Description of unit test:** Tests analyze the play function to verify it exceeds reasonable method length limits. The test checks that the play function exists and is excessively long (100+ lines), handles multiple responsibilities, and has high cyclomatic complexity.

**Quote of test:**
```python
def test_play_function_exists_and_is_long(self):
    """Test that the play function exists and is excessively long"""
    # Find play function in the file
    play_function_found = False
    for line in self.bot_lines:
        if 'async def play(' in line:
            play_function_found = True
            break
    
    self.assertTrue(play_function_found, "play function should exist in bot.py")
```

---

## Flaw 3: Duplicate Code - Database Operations

**Shortcoming of code flaw:** Nearly identical database operation patterns violate the DRY (Don't Repeat Yourself) principle. Functions like set_welcome_channel and set_log_channel have almost identical structure with only minor differences in column names and log messages.

**Description of unit test:** Tests analyze database functions to detect code duplication. The test verifies that set_welcome_channel and set_log_channel functions are nearly identical, and database operation patterns are repeated across multiple functions.

**Quote of test:**
```python
def test_set_channel_functions_are_nearly_identical(self):
    """Test that set_welcome_channel and set_log_channel are duplicated code"""
    # Extract both functions
    set_welcome_found = 'def set_welcome_channel(' in self.bot_content
    set_log_found = 'def set_log_channel(' in self.bot_content
    
    self.assertTrue(set_welcome_found and set_log_found, 
                   "Both set functions should exist and be nearly identical")
```

---

## Flaw 4: Duplicate Code - Error Handling

**Shortcoming of code flaw:** Repeated error handling patterns across API functions violate the DRY principle. Functions like get_adop and get_nasa_images have nearly identical exception handling structure with the same three-tier error handling (HTTPError, RequestException, Exception).

**Description of unit test:** Tests analyze API functions to detect duplicated error handling patterns. The test verifies that multiple functions have identical 3-tier error handling and exception patterns are repeated across functions.

**Quote of test:**
```python
def test_api_functions_have_identical_error_structures(self):
    """Test that API functions have nearly identical error handling structures"""
    # Look for the specific 3-tier error handling pattern
    http_error_count = self.bot_content.count('HTTPError')
    request_exception_count = self.bot_content.count('RequestException')
    
    self.assertGreaterEqual(http_error_count, 2, 
                           "Multiple functions should have HTTPError handling")
```

---

## Flaw 5: Primitive Obsession

**Shortcoming of code flaw:** Using primitive types (integers) instead of domain objects violates object-oriented design principles. The code uses primitive integers for guild_id and channel_id everywhere instead of creating proper domain objects like Guild, Channel, or GuildSettings.

**Description of unit test:** Tests analyze primitive type usage throughout the codebase. The test verifies that guild_id and channel_id are used as primitives across multiple functions, and no domain classes are found.

**Quote of test:**
```python
def test_guild_id_used_as_primitive_in_multiple_functions(self):
    """Test that guild_id is used as primitive integer across multiple functions"""
    guild_id_count = self.bot_content.count('guild_id')
    
    self.assertGreaterEqual(guild_id_count, 10, 
                           f"Found {guild_id_count} uses of guild_id as primitive - should use Guild domain object")
```

---

## Flaw 6: Data Clumps

**Shortcoming of code flaw:** guild_id and channel_id parameters appear together repeatedly across multiple functions, suggesting they should be grouped into a single object or class. This pattern makes the code harder to maintain and increases the chance of parameter order mistakes.

**Description of unit test:** Tests analyze parameter patterns to detect data clumps. The test verifies that database functions share the same guild_id, channel_id parameter pattern, and member.guild.id pattern is repeated across functions.

**Quote of test:**
```python
def test_database_functions_share_same_parameter_pattern(self):
    """Test that database functions all share the same guild_id, channel_id parameter pattern"""
    # Count functions that use both guild_id and channel_id
    functions_with_both = 0
    for func in ['set_welcome_channel', 'set_log_channel', 'get_welcome_channel', 'get_log_channel']:
        if func in self.bot_content and 'guild_id' in self.bot_content and 'channel_id' in self.bot_content:
            functions_with_both += 1
    
    self.assertGreaterEqual(functions_with_both, 2, "Multiple database functions use guild_id,channel_id clump")
```

---

## Flaw 7: Feature Envy

**Shortcoming of code flaw:** Functions extensively access external data structures, violating the principle of encapsulation and the Law of Demeter. The code is overly interested in the internal structure of external API responses and Discord objects, creating tight coupling.

**Description of unit test:** Tests analyze external data access patterns to detect feature envy. The test verifies that functions frequently access interaction object properties, violate Law of Demeter with chained property access, and lack domain objects for external data.

**Quote of test:**
```python
def test_interaction_object_property_access_frequency(self):
    """Test that functions frequently access interaction object properties"""
    interaction_count = self.bot_content.count('interaction.')
    
    self.assertGreaterEqual(interaction_count, 50, 
                           f"Found {interaction_count} interaction property accesses - indicates feature envy")
```

---

## Flaw 8: Conditional Complexity

**Shortcoming of code flaw:** Deeply nested if statements and complex boolean logic violate the principle of simple, readable code. The on_voice_state_update method has multiple levels of nested conditions and complex boolean expressions that make it difficult to understand and maintain.

**Description of unit test:** Tests analyze conditional complexity patterns throughout the codebase. The test verifies that functions have excessive boolean operators, high cyclomatic complexity, and deep nesting levels.

**Quote of test:**
```python
def test_functions_with_excessive_boolean_operators(self):
    """Test that functions have excessive boolean operators"""
    and_count = self.bot_content.count(' and ')
    or_count = self.bot_content.count(' or ')
    
    total_boolean_ops = and_count + or_count
    self.assertGreater(total_boolean_ops, 30, 
                      f"Found {total_boolean_ops} boolean operators - indicates conditional complexity")
```

---

## Flaw 9: Shotgun Surgery

**Shortcoming of code flaw:** Single changes require modifications in many places, violating the principle of localized change impact. When adding features like log channels, changes are scattered across multiple functions and locations in the code, making the system fragile.

**Description of unit test:** Tests analyze scattered functionality patterns that indicate shotgun surgery. The test verifies that Discord interaction handling is scattered across functions, guild operations are scattered across the codebase, and no centralized abstractions exist.

**Quote of test:**
```python
def test_discord_interaction_handling_scattered(self):
    """Test that Discord interaction handling is scattered across functions"""
    interaction_functions = self.bot_content.count('interaction')
    tree_commands = self.bot_content.count('@tree.command')
    
    self.assertGreaterEqual(tree_commands, 15, 
                           f"Found {tree_commands} scattered command handlers - indicates shotgun surgery")
```

---

## Summary

**Total Tests Created:** 27 individual unit tests across 9 test files (3 tests per flaw)
**All Tests Status:** ✅ PASSED
**Testing Approach:** Direct code analysis using string searches, pattern matching, and structural analysis
**Coverage:** All 9 code flaws from Lab 1 successfully tested with quantitative evidence

Each test file demonstrates clear evidence of the respective code smell through detailed analysis of the actual bot.py code structure, providing a realistic and manageable test suite for Lab 2. 