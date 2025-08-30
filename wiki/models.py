"""
SQLAlchemy Models for Mini-Wiki
Database schema using SQLAlchemy ORM with relationship mapping.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

# Association table for many-to-many relationship between entries and tags
entry_tags = Table('entry_tags', Base.metadata,
    Column('entry_id', Integer, ForeignKey('entries.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Category(Base):
    """Category model for organizing entries."""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Relationship
    entries = relationship("Entry", back_populates="category_obj")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"

class Tag(Base):
    """Tag model for labeling entries."""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    color = Column(String(7), default="#3498db")  # Hex color code
    created_at = Column(DateTime, default=func.now())
    
    # Relationship
    entries = relationship("Entry", secondary=entry_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"

class Entry(Base):
    """Main entry model for wiki entries."""
    __tablename__ = 'entries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    author = Column(String(100), default="Anonymous")
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    category_obj = relationship("Category", back_populates="entries")
    tags = relationship("Tag", secondary=entry_tags, back_populates="entries")
    
    @property
    def category(self):
        """Get category name for backward compatibility."""
        return self.category_obj.name if self.category_obj else ""
    
    def get_preview(self, max_length: int = 100) -> str:
        """Get a preview of the content with truncation."""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."
    
    def increment_views(self):
        """Increment view count with SQLAlchemy logic."""
        self.views += 1
    
    def to_dict(self) -> dict:
        """Convert entry to dictionary format."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'author': self.author,
            'views': self.views,
            'tags': [tag.name for tag in self.tags],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<Entry(id={self.id}, title='{self.title}', category='{self.category}')>"
