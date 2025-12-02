"""
Prompt templates and presets system for music generation
"""

from typing import Dict, List, Optional
from pathlib import Path
import json

class PromptTemplates:
    """Manage prompt templates and presets"""
    
    def __init__(self, templates_file: Optional[Path] = None):
        self.templates_file = templates_file or Path("prompt_templates.json")
        self.templates = self._load_templates()
        self._init_default_templates()
    
    def _load_templates(self) -> Dict:
        """Load templates from file"""
        if self.templates_file.exists():
            try:
                with open(self.templates_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading templates: {e}")
                return {}
        return {}
    
    def _save_templates(self):
        """Save templates to file"""
        with open(self.templates_file, "w", encoding="utf-8") as f:
            json.dump(self.templates, f, indent=2, ensure_ascii=False)
    
    def _init_default_templates(self):
        """Initialize default templates if file doesn't exist"""
        if not self.templates_file.exists():
            self.templates = {
                "genres": {
                    "synthwave": "A cyber-noir synthwave track with heavy bass and slow tempo",
                    "ambient": "A peaceful ambient soundscape with ethereal pads and gentle textures",
                    "lofi": "A lo-fi hip hop beat with vinyl crackle and mellow piano",
                    "dubstep": "An aggressive dubstep track with heavy bass drops and electronic elements",
                    "jazz": "A smooth jazz composition with saxophone and walking bass",
                    "rock": "An energetic rock track with electric guitar and powerful drums",
                    "classical": "A classical orchestral piece with strings and woodwinds",
                    "electronic": "An electronic dance track with synthesizers and rhythmic beats",
                    "metal": "A heavy metal track with distorted guitars and fast drums",
                    "reggae": "A reggae track with offbeat rhythm and bass guitar"
                },
                "moods": {
                    "energetic": "An energetic and upbeat track",
                    "melancholic": "A melancholic and emotional piece",
                    "mysterious": "A mysterious and atmospheric composition",
                    "uplifting": "An uplifting and inspiring melody",
                    "dark": "A dark and brooding soundscape",
                    "peaceful": "A peaceful and calming track",
                    "intense": "An intense and powerful composition",
                    "dreamy": "A dreamy and ethereal soundscape"
                },
                "instruments": {
                    "piano": "A piano-focused composition",
                    "guitar": "A guitar-driven track",
                    "drums": "A drum-heavy rhythm track",
                    "strings": "An orchestral strings arrangement",
                    "synthesizer": "A synthesizer-based electronic track",
                    "bass": "A bass-heavy track with deep low frequencies"
                },
                "styles": {
                    "cinematic": "A cinematic soundtrack suitable for film",
                    "video_game": "A video game music track with retro elements",
                    "background": "A background music track for content creation",
                    "focus": "A focus music track for productivity",
                    "meditation": "A meditation and relaxation track"
                },
                "presets": {
                    "cyberpunk": "A cyberpunk-themed track with synthesizers, heavy bass, and futuristic elements",
                    "space": "A space-themed ambient track with ethereal pads and cosmic textures",
                    "forest": "A nature-inspired track with organic sounds and ambient textures",
                    "city": "An urban soundscape with electronic elements and rhythmic patterns",
                    "ocean": "An ocean-themed ambient track with flowing textures and deep bass"
                }
            }
            self._save_templates()
    
    def get_template(self, category: str, name: str) -> Optional[str]:
        """Get a specific template"""
        return self.templates.get(category, {}).get(name)
    
    def get_category(self, category: str) -> Dict[str, str]:
        """Get all templates in a category"""
        return self.templates.get(category, {})
    
    def add_template(self, category: str, name: str, prompt: str):
        """Add a new template"""
        if category not in self.templates:
            self.templates[category] = {}
        self.templates[category][name] = prompt
        self._save_templates()
    
    def remove_template(self, category: str, name: str):
        """Remove a template"""
        if category in self.templates and name in self.templates[category]:
            del self.templates[category][name]
            self._save_templates()
    
    def list_categories(self) -> List[str]:
        """List all template categories"""
        return list(self.templates.keys())
    
    def search_templates(self, query: str) -> Dict[str, Dict[str, str]]:
        """Search templates by query"""
        results = {}
        query_lower = query.lower()
        
        for category, templates in self.templates.items():
            matches = {
                name: prompt
                for name, prompt in templates.items()
                if query_lower in name.lower() or query_lower in prompt.lower()
            }
            if matches:
                results[category] = matches
        
        return results
    
    def expand_prompt(self, prompt: str, variables: Optional[Dict[str, str]] = None) -> str:
        """
        Expand a prompt template with variables
        
        Example:
            prompt = "A {genre} track with {mood} feeling"
            variables = {"genre": "synthwave", "mood": "energetic"}
            Returns: "A synthwave track with energetic feeling"
        """
        if variables:
            return prompt.format(**variables)
        return prompt
    
    def combine_templates(
        self,
        genre: Optional[str] = None,
        mood: Optional[str] = None,
        instrument: Optional[str] = None,
        style: Optional[str] = None
    ) -> str:
        """Combine multiple template elements into a single prompt"""
        parts = []
        
        if genre:
            genre_prompt = self.get_template("genres", genre)
            if genre_prompt:
                parts.append(genre_prompt)
        
        if mood:
            mood_prompt = self.get_template("moods", mood)
            if mood_prompt:
                parts.append(mood_prompt)
        
        if instrument:
            inst_prompt = self.get_template("instruments", instrument)
            if inst_prompt:
                parts.append(inst_prompt)
        
        if style:
            style_prompt = self.get_template("styles", style)
            if style_prompt:
                parts.append(style_prompt)
        
        if not parts:
            return "A musical composition"
        
        return ". ".join(parts) + "."

