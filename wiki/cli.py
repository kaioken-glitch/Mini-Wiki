"""
Command Line Interface for Mini-Wiki
Handles user interaction, menus, prompts, and command processing.
"""

import sys
from typing import List, Optional
from .db_handler import DatabaseHandler
from .crud import WikiCRUD
from .entry import WikiEntry


class WikiCLI:
    """Command Line Interface for the Mini-Wiki application."""
    
    def __init__(self, db_handler: DatabaseHandler):
        """
        Initialize the CLI with database handler.
        
        Args:
            db_handler: DatabaseHandler instance
        """
        self.db_handler = db_handler
        self.crud = WikiCRUD(db_handler.get_connection())
        self.running = True
    
    def run(self) -> None:
        """Main CLI loop."""
        self.show_welcome()
        
        while self.running:
            try:
                self.show_menu()
                command = self.get_user_input("Choose a command: ").strip().lower()
                self.process_command(command)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for using Mini-Wiki!")
                self.running = False
            except Exception as e:
                print(f"❌ An error occurred: {e}")
                print("Please try again.")
    
    def show_welcome(self) -> None:
        """Display welcome message."""
        print("\n📚 Welcome to Mini-Wiki!")
        print("=" * 40)
        print("Your personal offline encyclopedia")
        print("Type 'help' for available commands\n")
    
    def show_menu(self) -> None:
        """Display the main menu options."""
        print("\n" + "─" * 40)
        print("🛠️  Available Commands:")
        print("   add     - Add a new entry")
        print("   view    - View all entries")
        print("   search  - Search entries")
        print("   update  - Update an entry")
        print("   delete  - Delete an entry")
        print("   stats   - Show database statistics")
        print("   help    - Show this menu")
        print("   exit    - Exit Mini-Wiki")
        print("─" * 40)
    
    def get_user_input(self, prompt: str) -> str:
        """
        Get user input with a prompt.
        
        Args:
            prompt: The prompt to display
            
        Returns:
            str: User input
        """
        return input(f"\n{prompt}")
    
    def process_command(self, command: str) -> None:
        """
        Process user commands.
        
        Args:
            command: The command to process
        """
        command_parts = command.split()
        base_command = command_parts[0] if command_parts else ""
        
        if base_command == "add":
            self.add_entry()
        elif base_command == "view":
            self.view_entries()
        elif base_command == "search":
            # Allow "search keyword" or just "search"
            keyword = " ".join(command_parts[1:]) if len(command_parts) > 1 else None
            self.search_entries(keyword)
        elif base_command == "update":
            # Allow "update id" or just "update"
            entry_id = command_parts[1] if len(command_parts) > 1 else None
            self.update_entry(entry_id)
        elif base_command == "delete":
            # Allow "delete id" or just "delete"
            entry_id = command_parts[1] if len(command_parts) > 1 else None
            self.delete_entry(entry_id)
        elif base_command == "stats":
            self.show_stats()
        elif base_command in ["help", "h", "?"]:
            self.show_help()
        elif base_command in ["exit", "quit", "q"]:
            self.exit_application()
        else:
            print(f"❌ Unknown command: '{command}'")
            print("Type 'help' to see available commands.")
    
    def add_entry(self) -> None:
        """Add a new entry through user prompts."""
        try:
            print("\n📝 Adding a new entry...")
            
            title = self.get_user_input("Title: ").strip()
            if not title:
                print("❌ Title cannot be empty!")
                return
            
            category = self.get_user_input("Category: ").strip()
            if not category:
                print("❌ Category cannot be empty!")
                return
            
            print("Content (press Enter twice to finish):")
            content_lines = []
            empty_lines = 0
            
            while empty_lines < 2:
                line = input()
                if line.strip() == "":
                    empty_lines += 1
                else:
                    empty_lines = 0
                content_lines.append(line)
            
            # Remove the last two empty lines
            content = "\n".join(content_lines[:-2]).strip()
            
            if not content:
                print("❌ Content cannot be empty!")
                return
            
            # Create the entry
            entry = self.crud.create_entry(title, category, content)
            print(f"✅ Entry added successfully! ID: {entry.id}")
            
        except Exception as e:
            print(f"❌ Failed to add entry: {e}")
    
    def view_entries(self) -> None:
        """View all entries with optional category filter."""
        try:
            # Ask if user wants to filter by category
            filter_choice = self.get_user_input("Filter by category? (y/n): ").strip().lower()
            
            category = None
            if filter_choice in ['y', 'yes']:
                categories = self.crud.get_categories()
                if categories:
                    print("\nAvailable categories:")
                    for i, cat in enumerate(categories, 1):
                        print(f"  {i}. {cat}")
                    
                    category = self.get_user_input("Enter category name: ").strip()
                    if category not in categories:
                        print(f"❌ Category '{category}' not found!")
                        return
            
            entries = self.crud.get_all_entries(category)
            
            if not entries:
                if category:
                    print(f"📭 No entries found in category '{category}'")
                else:
                    print("📭 No entries found. Add some entries to get started!")
                return
            
            print(f"\n📚 Found {len(entries)} entries:")
            print("=" * 60)
            
            for entry in entries:
                print(f"\n[{entry.id}] {entry.title}")
                print(f"Category: {entry.category}")
                print(f"Preview: {entry.get_preview(80)}")
                print(f"Created: {entry.created_at[:19].replace('T', ' ')}")
                print("-" * 40)
            
            # Option to view full entry
            entry_id = self.get_user_input("Enter entry ID to view full content (or press Enter to continue): ").strip()
            if entry_id.isdigit():
                self.view_full_entry(int(entry_id))
                
        except Exception as e:
            print(f"❌ Failed to view entries: {e}")
    
    def view_full_entry(self, entry_id: int) -> None:
        """View the full content of a specific entry."""
        try:
            entry = self.crud.get_entry_by_id(entry_id)
            if not entry:
                print(f"❌ Entry with ID {entry_id} not found!")
                return
            
            print("\n" + "=" * 60)
            print(f"📖 {entry.title}")
            print("=" * 60)
            print(f"Category: {entry.category}")
            print(f"Created: {entry.created_at[:19].replace('T', ' ')}")
            print(f"Updated: {entry.updated_at[:19].replace('T', ' ')}")
            print("-" * 60)
            print(entry.content)
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Failed to view entry: {e}")
    
    def search_entries(self, keyword: str = None) -> None:
        """Search entries by keyword."""
        try:
            if not keyword:
                keyword = self.get_user_input("Enter search keyword: ").strip()
            
            if not keyword:
                print("❌ Search keyword cannot be empty!")
                return
            
            entries = self.crud.search_entries(keyword)
            
            if not entries:
                print(f"🔍 No entries found matching '{keyword}'")
                return
            
            print(f"\n🔍 Found {len(entries)} entries matching '{keyword}':")
            print("=" * 60)
            
            for entry in entries:
                print(f"\n[{entry.id}] {entry.title}")
                print(f"Category: {entry.category}")
                print(f"Preview: {entry.get_preview(80)}")
                print("-" * 40)
            
            # Option to view full entry
            entry_id = self.get_user_input("Enter entry ID to view full content (or press Enter to continue): ").strip()
            if entry_id.isdigit():
                self.view_full_entry(int(entry_id))
                
        except Exception as e:
            print(f"❌ Failed to search entries: {e}")
    
    def update_entry(self, entry_id: str = None) -> None:
        """Update an existing entry."""
        try:
            if not entry_id:
                entry_id = self.get_user_input("Enter entry ID to update: ").strip()
            
            if not entry_id.isdigit():
                print("❌ Please enter a valid entry ID (number)!")
                return
            
            entry_id = int(entry_id)
            existing_entry = self.crud.get_entry_by_id(entry_id)
            
            if not existing_entry:
                print(f"❌ Entry with ID {entry_id} not found!")
                return
            
            print(f"\n✏️ Updating entry: {existing_entry.title}")
            print("Leave fields empty to keep current values")
            
            # Show current values and get new ones
            print(f"\nCurrent title: {existing_entry.title}")
            new_title = self.get_user_input("New title (or press Enter to keep current): ").strip()
            
            print(f"\nCurrent category: {existing_entry.category}")
            new_category = self.get_user_input("New category (or press Enter to keep current): ").strip()
            
            print(f"\nCurrent content:\n{existing_entry.content[:200]}...")
            update_content = self.get_user_input("Update content? (y/n): ").strip().lower()
            
            new_content = None
            if update_content in ['y', 'yes']:
                print("New content (press Enter twice to finish):")
                content_lines = []
                empty_lines = 0
                
                while empty_lines < 2:
                    line = input()
                    if line.strip() == "":
                        empty_lines += 1
                    else:
                        empty_lines = 0
                    content_lines.append(line)
                
                new_content = "\n".join(content_lines[:-2]).strip()
            
            # Update the entry
            updated_entry = self.crud.update_entry(
                entry_id,
                title=new_title if new_title else None,
                category=new_category if new_category else None,
                content=new_content if new_content else None
            )
            
            if updated_entry:
                print(f"✅ Entry updated successfully!")
            else:
                print(f"❌ Failed to update entry!")
                
        except Exception as e:
            print(f"❌ Failed to update entry: {e}")
    
    def delete_entry(self, entry_id: str = None) -> None:
        """Delete an entry."""
        try:
            if not entry_id:
                entry_id = self.get_user_input("Enter entry ID to delete: ").strip()
            
            if not entry_id.isdigit():
                print("❌ Please enter a valid entry ID (number)!")
                return
            
            entry_id = int(entry_id)
            existing_entry = self.crud.get_entry_by_id(entry_id)
            
            if not existing_entry:
                print(f"❌ Entry with ID {entry_id} not found!")
                return
            
            print(f"\n🗑️ You are about to delete:")
            print(f"Title: {existing_entry.title}")
            print(f"Category: {existing_entry.category}")
            
            confirmation = self.get_user_input("Are you sure? (yes/no): ").strip().lower()
            
            if confirmation == "yes":
                success = self.crud.delete_entry(entry_id)
                if success:
                    print("✅ Entry deleted successfully!")
                else:
                    print("❌ Failed to delete entry!")
            else:
                print("❌ Deletion cancelled.")
                
        except Exception as e:
            print(f"❌ Failed to delete entry: {e}")
    
    def show_stats(self) -> None:
        """Show database statistics."""
        try:
            db_info = self.db_handler.get_database_info()
            entry_count = self.crud.get_entry_count()
            categories = self.crud.get_categories()
            
            print("\n📊 Mini-Wiki Statistics:")
            print("=" * 40)
            print(f"📁 Database: {db_info['db_path']}")
            print(f"💾 Size: {db_info['db_size_mb']} MB")
            print(f"📝 Total entries: {entry_count}")
            print(f"🏷️ Categories: {len(categories)}")
            
            if categories:
                print("\nCategories:")
                for category in categories:
                    cat_entries = self.crud.get_all_entries(category)
                    print(f"  • {category}: {len(cat_entries)} entries")
            
        except Exception as e:
            print(f"❌ Failed to show statistics: {e}")
    
    def show_help(self) -> None:
        """Show detailed help information."""
        print("\n📚 Mini-Wiki Help")
        print("=" * 50)
        print("Commands:")
        print("  add              - Add a new wiki entry")
        print("  view             - View all entries (with optional category filter)")
        print("  search <keyword> - Search entries by keyword")
        print("  update <id>      - Update an existing entry")
        print("  delete <id>      - Delete an entry")
        print("  stats            - Show database statistics")
        print("  help             - Show this help message")
        print("  exit             - Exit the application")
        print("\nExamples:")
        print("  search python    - Search for entries containing 'python'")
        print("  update 5         - Update entry with ID 5")
        print("  delete 3         - Delete entry with ID 3")
        print("\nTips:")
        print("  • Use descriptive titles and categories")
        print("  • Press Enter twice to finish multi-line content")
        print("  • Use Ctrl+C to cancel any operation")
    
    def exit_application(self) -> None:
        """Exit the application gracefully."""
        print("\n👋 Thank you for using Mini-Wiki!")
        print("Your data has been saved. Goodbye!")
        self.running = False
