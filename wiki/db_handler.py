"""
Database Handler for Mini-Wiki
Manages SQLAlchemy database connection, schema setup, and database operations.
"""

import os
from typing import Optional
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from .models import Base, Category, Entry, Tag


class DatabaseHandler:
    """Handles database connection and schema management for Mini-Wiki using SQLAlchemy."""
    
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
        
        self.engine = None
        self.SessionLocal = None
        self._ensure_db_directory()
    
    def _ensure_db_directory(self) -> None:
        """Ensure the database directory exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def connect(self) -> None:
        """
        Establish connection to the database using SQLAlchemy.
        
        Raises:
            SQLAlchemyError: If connection fails
        """
        try:
            database_url = f"sqlite:///{self.db_path}"
            self.engine = create_engine(
                database_url,
                echo=False,  # Set to True for SQL debugging
                connect_args={"check_same_thread": False}  # Allow multi-threading
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to connect to database: {e}")
    
    def disconnect(self) -> None:
        """Close the database connection."""
        if self.engine:
            try:
                self.engine.dispose()
                self.engine = None
                self.SessionLocal = None
            except SQLAlchemyError as e:
                print(f"Warning: Error closing database connection: {e}")
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            Session: SQLAlchemy session object
        """
        if self.SessionLocal is None:
            self.connect()
        return self.SessionLocal()
    
    def initialize_database(self) -> None:
        """
        Initialize the database schema using SQLAlchemy.
        Creates tables if they don't exist and sets up default categories.
        
        Raises:
            SQLAlchemyError: If schema creation fails
        """
        try:
            if self.engine is None:
                self.connect()
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            # Create default categories if they don't exist
            session = self.get_session()
            try:
                default_categories = [
                    ("General", "General knowledge and miscellaneous topics"),
                    ("Technology", "Programming, software, and technical topics"),
                    ("Science", "Scientific concepts and discoveries"),
                    ("History", "Historical events and figures"),
                    ("Reference", "Quick reference materials and cheat sheets")
                ]
                
                for cat_name, cat_desc in default_categories:
                    existing = session.query(Category).filter_by(name=cat_name).first()
                    if not existing:
                        category = Category(name=cat_name, description=cat_desc)
                        session.add(category)
                
                session.commit()
                print(f"✅ Database initialized successfully at: {self.db_path}")
                
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to initialize database: {e}")
    
    def backup_database(self, backup_path: str) -> None:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Path where backup should be saved
            
        Raises:
            Exception: If backup fails
        """
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ Database backed up to: {backup_path}")
            
        except Exception as e:
            raise Exception(f"Failed to backup database: {e}")
    
    def vacuum_database(self) -> None:
        """
        Optimize the database by running VACUUM command.
        """
        try:
            session = self.get_session()
            try:
                session.execute(text("VACUUM"))
                session.commit()
                print("✅ Database optimized successfully")
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to vacuum database: {e}")
    
    def get_database_info(self) -> dict:
        """
        Get information about the database.
        
        Returns:
            dict: Database information including size, table count, etc.
        """
        try:
            session = self.get_session()
            try:
                # Get database file size
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                # Get entries count
                entries_count = session.query(Entry).count()
                
                # Get categories count
                categories_count = session.query(Category).count()
                
                # Get tags count
                tags_count = session.query(Tag).count()
                
                return {
                    'db_path': str(self.db_path),
                    'db_size_bytes': db_size,
                    'db_size_mb': round(db_size / (1024 * 1024), 2),
                    'entries_count': entries_count,
                    'categories_count': categories_count,
                    'tags_count': tags_count,
                    'exists': os.path.exists(self.db_path)
                }
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to get database info: {e}")
    
    def execute_query(self, query: str, params: dict = None) -> list:
        """
        Execute a custom query and return results.
        
        Args:
            query: SQL query to execute
            params: Parameters for the query
            
        Returns:
            list: Query results
            
        Raises:
            SQLAlchemyError: If query execution fails
        """
        try:
            session = self.get_session()
            try:
                result = session.execute(text(query), params or {})
                
                if query.strip().upper().startswith('SELECT'):
                    return result.fetchall()
                else:
                    session.commit()
                    return []
            finally:
                session.close()
                
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to execute query: {e}")
    
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
