"""
CRUD Operations for Mini-Wiki
Handles Create, Read, Update, Delete operations for wiki entries using SQLAlchemy ORM.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, func

from .models import Entry, Category, Tag
from .db_handler import DatabaseHandler


class WikiCRUD:
    """Handles all CRUD operations for wiki entries using SQLAlchemy ORM."""
    
    def __init__(self, db_handler: DatabaseHandler):
        """Initialize CRUD operations with database handler."""
        self.db_handler = db_handler
    
    def create_entry(self, title: str, category_name: str, content: str, author: str = "Anonymous") -> Entry:
        """
        Create a new wiki entry using SQLAlchemy ORM.
        
        Args:
            title: The title of the entry
            category_name: The category name for the entry
            content: The content of the entry
            author: The author of the entry
            
        Returns:
            Entry: The created entry with assigned ID
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        session = self.db_handler.get_session()
        try:
            # Get or create category
            category = session.query(Category).filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name, description=f"Auto-created category: {category_name}")
                session.add(category)
                session.flush()  # Get the ID
            
            # Create entry with SQLAlchemy logic
            entry = Entry(
                title=title,
                content=content,
                category_id=category.id,
                author=author
            )
            
            session.add(entry)
            session.commit()
            
            # Refresh to get the generated ID and relationships
            session.refresh(entry)
            return entry
            
        except SQLAlchemyError as e:
            session.rollback()
            raise SQLAlchemyError(f"Failed to create entry: {e}")
        finally:
            session.close()
    
    def get_entry_by_id(self, entry_id: int) -> Optional[Entry]:
        """
        Retrieve a single entry by its ID using SQLAlchemy ORM.
        
        Args:
            entry_id: The ID of the entry to retrieve
            
        Returns:
            Entry or None: The entry if found, None otherwise
        """
        session = self.db_handler.get_session()
        try:
            entry = session.query(Entry).filter_by(id=entry_id).first()
            if entry:
                # Apply SQLAlchemy logic - increment views
                entry.increment_views()
                session.commit()
            return entry
            
        except SQLAlchemyError as e:
            session.rollback()
            raise SQLAlchemyError(f"Failed to retrieve entry: {e}")
        finally:
            session.close()
    
    def get_all_entries(self, category_name: str = None) -> List[Entry]:
        """
        Retrieve all entries using SQLAlchemy ORM, optionally filtered by category.
        
        Args:
            category_name: Optional category filter
            
        Returns:
            List[Entry]: List of all matching entries
        """
        session = self.db_handler.get_session()
        try:
            query = session.query(Entry)
            
            if category_name:
                # Join with category table for filtering
                query = query.join(Category).filter(Category.name == category_name)
            
            # Order by creation date (most recent first)
            entries = query.order_by(Entry.created_at.desc()).all()
            return entries
            
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to retrieve entries: {e}")
        finally:
            session.close()
    
    def search_entries(self, keyword: str) -> List[Entry]:
        """
        Search for entries using SQLAlchemy ORM with OR conditions.
        
        Args:
            keyword: The search keyword
            
        Returns:
            List[Entry]: List of matching entries
        """
        session = self.db_handler.get_session()
        try:
            search_term = f"%{keyword}%"
            
            # Use SQLAlchemy ORM with OR conditions and joins
            entries = session.query(Entry).join(Category).filter(
                or_(
                    Entry.title.like(search_term),
                    Entry.content.like(search_term),
                    Category.name.like(search_term)
                )
            ).order_by(Entry.created_at.desc()).all()
            
            return entries
            
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to search entries: {e}")
        finally:
            session.close()
    
    def update_entry(self, entry_id: int, title: str = None, 
                    category_name: str = None, content: str = None, author: str = None) -> Optional[Entry]:
        """
        Update an existing entry using SQLAlchemy ORM.
        
        Args:
            entry_id: The ID of the entry to update
            title: New title (optional)
            category_name: New category name (optional)
            content: New content (optional)
            author: New author (optional)
            
        Returns:
            Entry or None: The updated entry if successful, None if not found
        """
        session = self.db_handler.get_session()
        try:
            # Get entry using SQLAlchemy ORM
            entry = session.query(Entry).filter_by(id=entry_id).first()
            if not entry:
                return None
            
            # Update fields if provided
            if title is not None:
                entry.title = title
            
            if category_name is not None:
                # Get or create category
                category = session.query(Category).filter_by(name=category_name).first()
                if not category:
                    category = Category(name=category_name, description=f"Auto-created category: {category_name}")
                    session.add(category)
                    session.flush()
                entry.category_id = category.id
            
            if content is not None:
                entry.content = content
                
            if author is not None:
                entry.author = author
            
            # SQLAlchemy will automatically update the updated_at timestamp due to onupdate
            session.commit()
            
            return entry
            
        except SQLAlchemyError as e:
            session.rollback()
            raise SQLAlchemyError(f"Failed to update entry: {e}")
        finally:
            session.close()
    
    def delete_entry(self, entry_id: int) -> bool:
        """
        Delete an entry using SQLAlchemy ORM.
        
        Args:
            entry_id: The ID of the entry to delete
            
        Returns:
            bool: True if deleted successfully, False if not found
        """
        session = self.db_handler.get_session()
        try:
            entry = session.query(Entry).filter_by(id=entry_id).first()
            if not entry:
                return False
            
            session.delete(entry)
            session.commit()
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            raise SQLAlchemyError(f"Failed to delete entry: {e}")
        finally:
            session.close()
    
    def get_entry_count(self) -> int:
        """
        Get the total number of entries using SQLAlchemy ORM.
        
        Returns:
            int: Total number of entries
        """
        session = self.db_handler.get_session()
        try:
            count = session.query(func.count(Entry.id)).scalar()
            return count
            
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to count entries: {e}")
        finally:
            session.close()
    
    def get_categories(self) -> List[str]:
        """
        Get all unique categories using SQLAlchemy ORM.
        
        Returns:
            List[str]: List of unique category names
        """
        session = self.db_handler.get_session()
        try:
            categories = session.query(Category.name).order_by(Category.name).all()
            return [cat[0] for cat in categories]
            
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to retrieve categories: {e}")
        finally:
            session.close()
    
    def add_tag_to_entry(self, entry_id: int, tag_name: str, color: str = "#3498db") -> bool:
        """
        Add a tag to an entry using SQLAlchemy ORM relationships.
        
        Args:
            entry_id: The entry ID
            tag_name: The tag name
            color: The tag color (hex code)
            
        Returns:
            bool: True if successful
        """
        session = self.db_handler.get_session()
        try:
            entry = session.query(Entry).filter_by(id=entry_id).first()
            if not entry:
                return False
            
            # Get or create tag
            tag = session.query(Tag).filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name, color=color)
                session.add(tag)
            
            # Add tag to entry if not already present
            if tag not in entry.tags:
                entry.tags.append(tag)
            
            session.commit()
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            raise SQLAlchemyError(f"Failed to add tag: {e}")
        finally:
            session.close()
    
    def get_entries_by_tag(self, tag_name: str) -> List[Entry]:
        """
        Get all entries with a specific tag using SQLAlchemy ORM relationships.
        
        Args:
            tag_name: The tag name
            
        Returns:
            List[Entry]: List of entries with the tag
        """
        session = self.db_handler.get_session()
        try:
            entries = session.query(Entry).join(Entry.tags).filter(Tag.name == tag_name).all()
            return entries
            
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to get entries by tag: {e}")
        finally:
            session.close()
