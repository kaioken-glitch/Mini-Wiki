"""
Wiki Entry Data Model
Represents a wiki entry with all its properties and methods.
"""

from typing import Dict
from datetime import datetime


class WikiEntry:
    """Represents a wiki entry with all its properties."""
    
    def __init__(self, id: int = None, title: str = "", category: str = "", 
                 content: str = "", created_at: str = None, updated_at: str = None):
        self.id = id
        self.title = title
        self.category = category
        self.content = content
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert entry to dictionary format."""
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'content': self.content,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def __str__(self) -> str:
        """String representation of the entry."""
        return f"[{self.id}] {self.title} ({self.category})"
    
    def __repr__(self) -> str:
        """Developer-friendly representation of the entry."""
        return f"WikiEntry(id={self.id}, title='{self.title}', category='{self.category}')"
    
    def get_preview(self, max_length: int = 100) -> str:
        """Get a preview of the content with truncation."""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.now().isoformat()
