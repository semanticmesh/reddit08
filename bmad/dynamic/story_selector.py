
import os
import yaml
from typing import List, Dict, Any

class StorySelector:
    """
    Selects a BMAD story to execute based on defined criteria.
    """
    def __init__(self, stories_dir: str = "bmad/stories"):
        # Adjust stories_dir to be relative to this script's location
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.stories_dir = os.path.join(base_dir, stories_dir)
        self.stories = self._load_stories()

    def _load_stories(self) -> List[Dict[str, Any]]:
        """
        Loads all BMAD stories from the specified directory.
        It reads from a single text file that contains multiple YAML documents.
        """
        stories_file = os.path.join(self.stories_dir, "bmad_stories.txt")
        if not os.path.exists(stories_file):
            print(f"Stories file not found at: {stories_file}")
            return []

        with open(stories_file, "r") as f:
            content = f.read()
        
        # Split the content by the YAML document separator '---'
        story_docs = content.strip().split("\n---\n")
        
        loaded_stories = []
        for doc in story_docs:
             # Clean up the document string
            doc_content = doc.strip()
            if not doc_content or doc_content.startswith("#"):
                continue
            # Remove comment lines before parsing
            doc_clean = "\n".join(line for line in doc_content.splitlines() if not line.strip().startswith('#'))

            try:
                story = yaml.safe_load(doc_clean)
                if isinstance(story, dict):
                    loaded_stories.append(story)
            except yaml.YAMLError as e:
                print(f"Error parsing YAML document: {e}")
        
        return loaded_stories

    def list_stories(self) -> List[str]:
        """
        Returns a list of available story names.
        """
        return [story.get("name", "Unnamed Story") for story in self.stories if story]

    def select_story(self, story_name: str) -> Dict[str, Any]:
        """
        Selects a story by its name.
        """
        for story in self.stories:
            if story and story.get("name") == story_name:
                return story
        return None

    def select_by_priority(self, priority: str = "P0") -> List[Dict[str, Any]]:
        """
        Selects stories based on a specific priority level.
        """
        return [story for story in self.stories if story and story.get("priority") == priority]

if __name__ == "__main__":
    # The stories directory is located relative to the script's execution path.
    # When running from `C:\Users\pigna\yuandao\reddit08\bmad\dynamic`,
    # the stories folder is at `../../bmad/stories` which simplifies to `../stories`
    # To make it robust, we assume the script is in `bmad/dynamic` and stories in `bmad/stories`
    selector = StorySelector(stories_dir='stories')
    
    print("Available Stories:")
    for name in selector.list_stories():
        print(f"- {name}")
        
    print("\nSelecting P0 priority stories:")
    p0_stories = selector.select_by_priority("P0")
    for story in p0_stories:
        print(f"- {story.get('name')} ({story.get('id')})")

    print("\nSelecting a specific story by name 'Phrase Miner':")
    phrase_miner_story = selector.select_story("Phrase Miner")
    if phrase_miner_story:
        print(yaml.dump(phrase_miner_story, default_flow_style=False, indent=2))
