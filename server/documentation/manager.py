"""
Documentation Manager for PlayAural.
Handles loading and serving markdown documentation files.
"""

import os
from pathlib import Path
from typing import Optional, Dict

class DocumentationManager:
    """Singleton to manage documentation content."""
    
    _instance = None
    _content_cache: Dict[str, Dict[str, str]] = {} # locale -> { doc_id -> content }
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        self.base_path = Path(__file__).parent / "content"

    def get_document(self, doc_id: str, locale: str = "en") -> Optional[str]:
        """
        Get the content of a document by ID and locale.
        Falls back to 'en' if localized version is missing.
        
        Args:
            doc_id: Document identifier (e.g., 'intro', 'games/scopa')
            locale: Language code (default 'en')
            
        Returns:
            String content of the markdown file, or None if not found.
        """
        # Try requested locale
        content = self._load_file(doc_id, locale)
        if content:
            return content
            
        # Fallback to English if not 'en'
        if locale != "en":
            return self._load_file(doc_id, "en")
            
        return None

    def _load_file(self, doc_id: str, locale: str) -> Optional[str]:
        """Helper to load a raw file."""
        try:
            # Prevent directory traversal
            if ".." in doc_id:
                return None
                
            file_path = self.base_path / locale / f"{doc_id}.md"
            if file_path.exists() and file_path.is_file():
                return file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error loading documentation {doc_id} ({locale}): {e}")
            return None

    def get_all_categories(self, locale: str = "en") -> Dict[str, str]:
        """
        Get a list of available top-level documentation categories.
        Realistically this might be hardcoded, but here we'll define standard ones.
        """
        return {
            "intro": "introduction",
            "community_rules": "community-rules", 
            "global_keys": "global-keys",
        }
