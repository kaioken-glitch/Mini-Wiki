"""
CRUD Operations for Mini-Wiki
Handles Create, Read, Update, Delete operations for wiki entries.
"""

import sqlite3
from typing import List, Optional
from datetime import datetime

from .entry import WikiEntry


class WikiCRUD:
    """Handles all CRUD operations for wiki entries."""
    
    def __init__(self, db_connection: sqlite3.Connection):
        """Initialize CRUD operations with database connection."""
        self.conn = db_connection
    
    def create_entry(self, title: str, category: str, content: str) -> WikiEntry:
        """
        Create a new wiki entry.
        
        Args:
            title: The title of the entry
            category: The category of the entry
            content: The content of the entry
            
        Returns:
            WikiEntry: The created entry with assigned ID
            
        Raises:
            sqlite3.Error: If database operation fails
        """
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO entries (title, category, content, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (title, category, content, now, now))
            
            self.conn.commit()
            entry_id = cursor.lastrowid
            
            return WikiEntry(
                id=entry_id,
                title=title,
                category=category,
                content=content,
                created_at=now,
                updated_at=now
            )
            
        except sqlite3.Error as e:
            self.conn.rollback()
            raise sqlite3.Error(f"Failed to create entry: {e}")
    
    def get_entry_by_id(self, entry_id: int) -> Optional[WikiEntry]:
        """
        Retrieve a single entry by its ID.
        
        Args:
            entry_id: The ID of the entry to retrieve
            
        Returns:
            WikiEntry or None: The entry if found, None otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, title, category, content, created_at, updated_at
                FROM entries WHERE id = ?
            """, (entry_id,))
            
            row = cursor.fetchone()
            if row:
                return WikiEntry(*row)
            return None
            
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to retrieve entry: {e}")
    
    def get_all_entries(self, category: str = None) -> List[WikiEntry]:
        """
        Retrieve all entries, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            List[WikiEntry]: List of all matching entries
        """
        try:
            cursor = self.conn.cursor()
            
            if category:
                cursor.execute("""
                    SELECT id, title, category, content, created_at, updated_at
                    FROM entries WHERE category = ?
                    ORDER BY created_at DESC
                """, (category,))
            else:
                cursor.execute("""
                    SELECT id, title, category, content, created_at, updated_at
                    FROM entries ORDER BY created_at DESC
                """)
            
            rows = cursor.fetchall()
            return [WikiEntry(*row) for row in rows]
            
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to retrieve entries: {e}")
    
    def search_entries(self, keyword: str) -> List[WikiEntry]:
        """
        Search for entries containing the keyword in title, category, or content.
        
        Args:
            keyword: The search keyword
            
        Returns:
            List[WikiEntry]: List of matching entries
        """
        try:
            cursor = self.conn.cursor()
            search_term = f"%{keyword}%"
            
            cursor.execute("""
                SELECT id, title, category, content, created_at, updated_at
                FROM entries 
                WHERE title LIKE ? OR category LIKE ? OR content LIKE ?
                ORDER BY created_at DESC
            """, (search_term, search_term, search_term))
            
            rows = cursor.fetchall()
            return [WikiEntry(*row) for row in rows]
            
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to search entries: {e}")
    
    def update_entry(self, entry_id: int, title: str = None, 
                    category: str = None, content: str = None) -> Optional[WikiEntry]:
        """
        Update an existing entry.
        
        Args:
            entry_id: The ID of the entry to update
            title: New title (optional)
            category: New category (optional)
            content: New content (optional)
            
        Returns:
            WikiEntry or None: The updated entry if successful, None if not found
        """
        try:
            # First check if entry exists
            existing_entry = self.get_entry_by_id(entry_id)
            if not existing_entry:
                return None
            
            # Prepare update values (keep existing values if not provided)
            new_title = title if title is not None else existing_entry.title
            new_category = category if category is not None else existing_entry.category
            new_content = content if content is not None else existing_entry.content
            new_updated_at = datetime.now().isoformat()
            
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE entries 
                SET title = ?, category = ?, content = ?, updated_at = ?
                WHERE id = ?
            """, (new_title, new_category, new_content, new_updated_at, entry_id))
            
            self.conn.commit()
            
            # Return updated entry
            return WikiEntry(
                id=entry_id,
                title=new_title,
                category=new_category,
                content=new_content,
                created_at=existing_entry.created_at,
                updated_at=new_updated_at
            )
            
        except sqlite3.Error as e:
            self.conn.rollback()
            raise sqlite3.Error(f"Failed to update entry: {e}")
    
    def delete_entry(self, entry_id: int) -> bool:
        """
        Delete an entry by its ID.
        
        Args:
            entry_id: The ID of the entry to delete
            
        Returns:
            bool: True if deleted successfully, False if not found
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
            self.conn.commit()
            
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            self.conn.rollback()
            raise sqlite3.Error(f"Failed to delete entry: {e}")
    
    def get_entry_count(self) -> int:
        """
        Get the total number of entries.
        
        Returns:
            int: Total number of entries
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM entries")
            return cursor.fetchone()[0]
            
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to count entries: {e}")
    
    def get_categories(self) -> List[str]:
        """
        Get all unique categories.
        
        Returns:
            List[str]: List of unique categories
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM entries ORDER BY category")
            return [row[0] for row in cursor.fetchall()]
            
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to retrieve categories: {e}")
