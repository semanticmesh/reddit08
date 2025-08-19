import pytest
import os
import sys
import yaml
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dynamic.story_selector import StorySelector


class TestStorySelector:
    """Test suite for the StorySelector class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_stories_dir = os.path.join(os.path.dirname(__file__), 'test_data', 'stories')
        os.makedirs(self.test_stories_dir, exist_ok=True)
        
        # Create test stories file
        self.test_stories_content = """
---
id: TEST-01
name: Test Story 1
priority: P0
description: A test story for unit testing
tasks:
  - action: test_action
    parameters: {}
---
id: TEST-02
name: Test Story 2
priority: P1
description: Another test story
tasks:
  - action: another_action
    parameters: {param1: value1}
"""
        
        self.test_stories_file = os.path.join(self.test_stories_dir, 'test_stories.txt')
        with open(self.test_stories_file, 'w') as f:
            f.write(self.test_stories_content)
            
        # Initialize StorySelector with test directory
        self.selector = StorySelector(stories_dir=os.path.join('test_data', 'stories'))
        
    def teardown_method(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_stories_file):
            os.remove(self.test_stories_file)
        if os.path.exists(self.test_stories_dir):
            os.rmdir(self.test_stories_dir)
        if os.path.exists(os.path.dirname(self.test_stories_dir)):
            os.rmdir(os.path.dirname(self.test_stories_dir))
            
    def test_load_stories(self):
        """Test that stories are loaded correctly."""
        stories = self.selector.stories
        assert len(stories) == 2
        
        # Check first story
        story1 = stories[0]
        assert story1['id'] == 'TEST-01'
        assert story1['name'] == 'Test Story 1'
        assert story1['priority'] == 'P0'
        assert 'tasks' in story1
        
        # Check second story
        story2 = stories[1]
        assert story2['id'] == 'TEST-02'
        assert story2['name'] == 'Test Story 2'
        assert story2['priority'] == 'P1'
        
    def test_list_stories(self):
        """Test listing story names."""
        story_names = self.selector.list_stories()
        expected_names = ['Test Story 1', 'Test Story 2']
        assert len(story_names) == 2
        assert 'Test Story 1' in story_names
        assert 'Test Story 2' in story_names
        
    def test_select_story_by_name(self):
        """Test selecting a story by name."""
        story = self.selector.select_story('Test Story 1')
        assert story is not None
        assert story['name'] == 'Test Story 1'
        assert story['id'] == 'TEST-01'
        
        # Test non-existent story
        story = self.selector.select_story('Non-existent Story')
        assert story is None
        
    def test_select_by_priority(self):
        """Test selecting stories by priority."""
        p0_stories = self.selector.select_by_priority('P0')
        p1_stories = self.selector.select_by_priority('P1')
        
        assert len(p0_stories) == 1
        assert p0_stories[0]['name'] == 'Test Story 1'
        
        assert len(p1_stories) == 1
        assert p1_stories[0]['name'] == 'Test Story 2'
        
        # Test non-existent priority
        p2_stories = self.selector.select_by_priority('P2')
        assert len(p2_stories) == 0
        
    def test_empty_stories_file(self):
        """Test behavior with empty or missing stories file."""
        # Create empty file
        empty_file = os.path.join(self.test_stories_dir, 'empty_stories.txt')
        with open(empty_file, 'w') as f:
            f.write('')
            
        # Create selector with empty file
        selector = StorySelector(stories_dir=os.path.join('test_data', 'stories'))
        assert len(selector.stories) == 0
        
        # Clean up
        os.remove(empty_file)
        
    def test_invalid_yaml(self):
        """Test handling of invalid YAML content."""
        # Create file with invalid YAML
        invalid_yaml_file = os.path.join(self.test_stories_dir, 'invalid_stories.txt')
        with open(invalid_yaml_file, 'w') as f:
            f.write("""
---
id: TEST-01
name: Valid Story
priority: P0
---
# This is invalid YAML
invalid: content: [unclosed bracket
---
id: TEST-02
name: Another Valid Story
priority: P1
""")
        
        # Create selector with invalid YAML file
        selector = StorySelector(stories_dir=os.path.join('test_data', 'stories'))
        # Should still load valid stories and ignore invalid ones
        assert len(selector.stories) >= 1  # At least one valid story should be loaded
        
        # Clean up
        os.remove(invalid_yaml_file)
