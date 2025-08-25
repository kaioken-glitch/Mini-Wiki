"""
Mini-Wiki CLI - Entry Point
A simple command-line wiki for storing and managing knowledge entries.
"""

import sys
import os

# Add the wiki package to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from wiki.cli import WikiCLI
from wiki.db_handler import DatabaseHandler


def main():
    """Main entry point for the Mini-Wiki CLI application."""
    print("📚 Welcome to Mini-Wiki!")
    print("=" * 40)
    
    # Initialize database
    try:
        db_handler = DatabaseHandler()
        db_handler.initialize_database()
        
        # Start the CLI
        cli = WikiCLI(db_handler)
        cli.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using Mini-Wiki!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting Mini-Wiki: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
