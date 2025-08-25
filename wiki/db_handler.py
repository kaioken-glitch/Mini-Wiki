"""
Database Handler for Mini-Wiki
Manages SQLite database connection, schema setup, and database operations.
"""

import sqlite3
import os
from typing import Optional
from pathlib import Path


class DatabaseHandler:
    """Handles database connection and schema management for Mini-Wiki."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize database handler.
        
        Args:
            db_path: Path to the database file. If None, uses default path.
        """
        if db_path is None:
            # Create db directory if it doesn't exist
            db_dir = Path(__file__).parent.parent / "db"
            db_dir.mkdir(exist_ok=True)
            self.db_path = db_dir / "wiki.db"
        else:
            self.db_path = Path(db_path)
        
        self.connection: Optional[sqlite3.Connection] = None
        self._ensure_db_directory()
    
    def _ensure_db_directory(self) -> None:
        """Ensure the database directory exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def connect(self) -> sqlite3.Connection:
        """
        Establish connection to the database.
        
        Returns:
            sqlite3.Connection: Database connection object
            
        Raises:
            sqlite3.Error: If connection fails
        """
        try:
            self.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,  # Allow multi-threading
                timeout=30.0  # 30 second timeout
            )
            
            # Enable foreign key constraints
            self.connection.execute("PRAGMA foreign_keys = ON")
            
            # Set row factory for easier data access
            self.connection.row_factory = sqlite3.Row
            
            return self.connection
            
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to connect to database: {e}")
    
    def disconnect(self) -> None:
        """Close the database connection."""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
            except sqlite3.Error as e:
                print(f"Warning: Error closing database connection: {e}")
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get the current database connection, creating one if needed.
        
        Returns:
            sqlite3.Connection: Active database connection
        """
        if self.connection is None:
            self.connect()
        return self.connection
    
    def initialize_database(self) -> None:
        """
        Initialize the database schema.
        Creates tables if they don't exist.
        
        Raises:
            sqlite3.Error: If schema creation fails
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create entries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(title, category)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_entries_title 
                ON entries(title)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_entries_category 
                ON entries(category)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_entries_created_at 
                ON entries(created_at)
            """)
            
            # Create full-text search virtual table for content search
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts USING fts5(
                    title, category, content,
                    content='entries',
                    content_rowid='id'
                )
            """)
            
            # Create triggers to keep FTS table in sync
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS entries_ai AFTER INSERT ON entries BEGIN
                    INSERT INTO entries_fts(rowid, title, category, content) 
                    VALUES (new.id, new.title, new.category, new.content);
                END
            """)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS entries_ad AFTER DELETE ON entries BEGIN
                    INSERT INTO entries_fts(entries_fts, rowid, title, category, content) 
                    VALUES('delete', old.id, old.title, old.category, old.content);
                END
            """)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS entries_au AFTER UPDATE ON entries BEGIN
                    INSERT INTO entries_fts(entries_fts, rowid, title, category, content) 
                    VALUES('delete', old.id, old.title, old.category, old.content);
                    INSERT INTO entries_fts(rowid, title, category, content) 
                    VALUES (new.id, new.title, new.category, new.content);
                END
            """)
            
            conn.commit()
            print(f"✅ Database initialized successfully at: {self.db_path}")
            
        except sqlite3.Error as e:
            if self.connection:
                self.connection.rollback()
            raise sqlite3.Error(f"Failed to initialize database: {e}")
    
    def backup_database(self, backup_path: str) -> None:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Path where backup should be saved
            
        Raises:
            sqlite3.Error: If backup fails
        """
        try:
            conn = self.get_connection()
            backup_conn = sqlite3.connect(backup_path)
            
            conn.backup(backup_conn)
            backup_conn.close()
            
            print(f"✅ Database backed up to: {backup_path}")
            
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to backup database: {e}")
    
    def vacuum_database(self) -> None:
        """
        Optimize the database by running VACUUM command.
        This rebuilds the database file, repacking it into a minimal amount of disk space.
        """
        try:
            conn = self.get_connection()
            conn.execute("VACUUM")
            print("✅ Database optimized successfully")
            
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to vacuum database: {e}")
    
    def get_database_info(self) -> dict:
        """
        Get information about the database.
        
        Returns:
            dict: Database information including size, table count, etc.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get database file size
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            # Get table count
            cursor.execute("""
                SELECT COUNT(*) FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            table_count = cursor.fetchone()[0]
            
            # Get entries count
            cursor.execute("SELECT COUNT(*) FROM entries")
            entries_count = cursor.fetchone()[0]
            
            return {
                'db_path': str(self.db_path),
                'db_size_bytes': db_size,
                'db_size_mb': round(db_size / (1024 * 1024), 2),
                'table_count': table_count,
                'entries_count': entries_count,
                'exists': os.path.exists(self.db_path)
            }
            
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to get database info: {e}")
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """
        Execute a custom query and return results.
        
        Args:
            query: SQL query to execute
            params: Parameters for the query
            
        Returns:
            list: Query results
            
        Raises:
            sqlite3.Error: If query execution fails
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                conn.commit()
                return []
                
        except sqlite3.Error as e:
            if self.connection:
                self.connection.rollback()
            raise sqlite3.Error(f"Failed to execute query: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def __del__(self):
        """Destructor to ensure connection is closed."""
        self.disconnect()
