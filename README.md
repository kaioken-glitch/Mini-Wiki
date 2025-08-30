
# � Mini-Wiki CLI

A sophisticated command-line wiki application built with Python, SQLAlchemy ORM, and Alembic migrations. Store, search, and manage your knowledge entries with an intuitive CLI interface.

[![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-blue.svg)](https://sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-Migrations-orange.svg)](https://alembic.sqlalchemy.org/)
[![CLI](https://img.shields.io/badge/CLI-Tool-purple.svg)](https://github.com)

---

## ✨ Features

- **📝 Entry Management** — Create, read, update, and delete wiki entries
- **🏷️ Categories & Tags** — Organize entries with categories and flexible tagging system
- **🔍 Advanced Search** — Search across titles, content, categories, and tags
- **👤 Author Tracking** — Track entry authors and view counts
- **� Statistics** — View database statistics and analytics
- **🗃️ SQLAlchemy ORM** — Robust database operations with relationships
- **🔄 Alembic Migrations** — Database schema versioning and migrations
- **💾 Offline Ready** — Works completely offline with SQLite database

## 🏗️ Architecture

### Database Schema (SQLAlchemy ORM)

The application uses SQLAlchemy ORM with three main tables:

#### **Entries Table**
- `id`: Primary key (auto-increment)
- `title`: Entry title (string, required)
- `content`: Entry content (text, required)  
- `category_id`: Foreign key to categories table
- `author`: Entry author (string, default: "Anonymous")
- `views`: View count (integer, default: 0)
- `created_at`: Creation timestamp (auto-generated)
- `updated_at`: Last update timestamp (auto-updated)

#### **Categories Table**
- `id`: Primary key (auto-increment)
- `name`: Category name (unique string, required)
- `description`: Category description (text)
- `created_at`: Creation timestamp (auto-generated)

#### **Tags Table**
- `id`: Primary key (auto-increment)
- `name`: Tag name (unique string, required)
- `color`: Hex color code (string, default: "#3498db")
- `created_at`: Creation timestamp (auto-generated)

#### **Entry-Tags Association Table**
- Many-to-many relationship between entries and tags
- `entry_id`: Foreign key to entries table
- `tag_id`: Foreign key to tags table

## 📂 Project Structure

```
mini-wiki/
├── README.md                 # Project documentation
├── main.py                   # CLI application entry point
├── Pipfile                   # Pipenv dependencies
├── alembic.ini               # Alembic configuration
├── alembic/                  # Database migrations
│   ├── env.py               # Migration environment
│   ├── script.py.mako       # Migration template
│   └── versions/            # Migration files
├── db/
│   └── wiki.db              # SQLite database (auto-created)
└── wiki/                    # Main package
    ├── __init__.py          # Package initialization
    ├── models.py            # SQLAlchemy ORM models
    ├── db_handler.py        # Database connection & session management
    ├── crud.py              # CRUD operations with ORM
    ├── cli.py               # Command-line interface
    └── entry.py             # Legacy entry model (deprecated)
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Pipenv (recommended) or pip

### Using Pipenv (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd mini-wiki

# Install dependencies
pipenv install

# Activate virtual environment
pipenv shell

# Initialize database
python main.py
```

### Using pip

```bash
# Clone the repository
git clone <repository-url>
cd mini-wiki

# Install dependencies
pip install sqlalchemy alembic click colorama

# Initialize database
python main.py
```

## 📋 Usage Guide

### Starting the Application

```bash
python main.py
```

### Available Commands

#### **Main Menu Commands**
- `add` — Add a new wiki entry
- `view` — View all entries (with optional category filter)
- `search <keyword>` — Search entries by keyword
- `update <id>` — Update an existing entry
- `delete <id>` — Delete an entry
- `stats` — Show database statistics
- `help` — Show command help
- `exit` — Exit the application

### Function Workflow

#### **Adding an Entry (`add` command)**
1. **User Input Validation**: Prompts for title, category, and content
2. **Category Management**: Automatically creates new categories if they don't exist
3. **Database Operation**: Uses SQLAlchemy ORM to create new Entry object
4. **Relationship Handling**: Links entry to category via foreign key
5. **Transaction Management**: Commits changes with automatic rollback on errors

#### **Viewing Entries (`view` command)**
1. **Category Filtering**: Optional filter by existing categories
2. **ORM Query**: Uses SQLAlchemy join operations for efficient retrieval
3. **Data Presentation**: Displays entries with metadata (author, views, tags)
4. **Pagination Support**: Handles large result sets gracefully
5. **View Tracking**: Automatically increments view count when accessing entries

#### **Searching Entries (`search` command)**
1. **Multi-field Search**: Searches across title, content, and category fields
2. **ORM Relationships**: Joins tables for comprehensive search results
3. **Pattern Matching**: Uses SQL LIKE operations for flexible matching
4. **Result Ranking**: Orders results by relevance and creation date

#### **Updating Entries (`update` command)**
1. **Entry Retrieval**: Fetches existing entry using ORM
2. **Selective Updates**: Only updates provided fields, preserves others
3. **Category Migration**: Handles category changes with relationship updates
4. **Timestamp Management**: Automatically updates `updated_at` timestamp
5. **Data Validation**: Ensures data integrity throughout update process

#### **Deleting Entries (`delete` command)**
1. **Confirmation Process**: Requires explicit user confirmation
2. **Cascade Operations**: Handles related data (tags, relationships) properly
3. **Transaction Safety**: Uses database transactions for data consistency
4. **Cleanup Operations**: Removes orphaned relationships automatically

#### **Statistics (`stats` command)**
1. **Database Metrics**: Calculates entry counts, categories, and tags
2. **File Information**: Shows database file size and location
3. **Category Breakdown**: Lists entries per category with counts
4. **Performance Data**: Displays query execution statistics

## 🔧 Database Management

### Alembic Migrations

```bash
# Generate a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# View migration history
alembic history

# Downgrade to previous version
alembic downgrade -1
```

### Database Operations

```bash
# Backup database
python -c "from wiki.db_handler import DatabaseHandler; db = DatabaseHandler(); db.backup_database('backup.db')"

# Optimize database
python -c "from wiki.db_handler import DatabaseHandler; db = DatabaseHandler(); db.vacuum_database()"
```

## 🎯 Data Structures Used

### **Lists**
- **Command Processing**: `command.split()` creates list of command parts
- **Content Input**: Multi-line content stored in `content_lines = []` list
- **Search Results**: Query results returned as `List[Entry]` objects
- **Category Management**: Categories retrieved as `List[str]` for display
- **Tag Collections**: Entry tags accessed as list via SQLAlchemy relationships

### **Dictionaries**
- **Database Info**: `get_database_info()` returns dict with metadata
- **Entry Serialization**: `to_dict()` method converts entry to dictionary format
- **Query Parameters**: SQLAlchemy query parameters passed as dict
- **Configuration**: Database connection settings stored in dict format

### **Tuples**
- **SQL Parameters**: Query parameters passed as tuples to prevent SQL injection
- **Table Relationships**: Primary/foreign key pairs stored as tuples
- **Enumeration**: `enumerate(categories, 1)` returns tuple pairs for indexing
- **Default Categories**: Initial categories defined as list of tuples

## 🧪 CLI Best Practices Implementation

### **Separation of Concerns**
- **Entry Point** (`main.py`): Pure script for application bootstrapping
- **Business Logic** (`crud.py`, `models.py`): Object-oriented database operations
- **User Interface** (`cli.py`): Clean separation of UI from business logic
- **Data Layer** (`db_handler.py`): Isolated database connection management

### **Input Validation**
- **Required Fields**: Validates title, category, and content are not empty
- **Data Types**: Ensures entry IDs are numeric before processing
- **User Confirmation**: Requires explicit confirmation for destructive operations
- **Error Handling**: Graceful handling of database errors with user-friendly messages

### **User Experience**
- **Clear Prompts**: Descriptive prompts guide users through operations
- **Progress Feedback**: Success/error messages with emoji indicators
- **Help System**: Comprehensive help with examples and usage patterns
- **Graceful Exit**: Proper cleanup and goodbye messages on exit

## 🛠️ Dependencies

### **Core Dependencies** (in Pipfile)
- **SQLAlchemy**: ORM for database operations and relationships
- **Alembic**: Database migration and schema versioning
- **Click**: Enhanced command-line interface utilities  
- **Colorama**: Cross-platform colored terminal output

### **Built-in Libraries**
- **sqlite3**: Database backend (via SQLAlchemy)
- **datetime**: Timestamp management
- **pathlib**: Cross-platform file path handling
- **typing**: Type hints for better code quality

## � Example Usage

```bash
# Start the application
python main.py

# Add a new entry
> add
Title: Python SQLAlchemy Tutorial
Category: Technology
Content: SQLAlchemy is a powerful ORM for Python...
✅ Entry added successfully! ID: 1

# Search entries
> search SQLAlchemy
🔍 Found 1 entries matching 'SQLAlchemy'

# View statistics
> stats
📊 Mini-Wiki Statistics:
📁 Database: /path/to/wiki.db
💾 Size: 0.02 MB
📝 Total entries: 1
🏷️ Categories: 1
🏆 Tags: 0
```

## 🚀 Advanced Features

- **View Tracking**: Automatic view count increment with SQLAlchemy logic
- **Tag System**: Flexible tagging with color coding support
- **Category Auto-creation**: Dynamic category creation during entry addition
- **Relationship Management**: Proper handling of many-to-many relationships
- **Transaction Safety**: Automatic rollback on errors with proper exception handling

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests (if available)
5. Create a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*Built with ❤️ using Python, SQLAlchemy, and modern CLI design principles.*


## 🛠️ Commands
<ul>
	<li><b>add</b> &mdash; Adds a new entry</li>
	<li><b>view</b> &mdash; View all entries</li>
	<li><b>search &lt;Keyword&gt;</b> &mdash; Search for entries by keyword</li>
	<li><b>update &lt;id&gt;</b> &mdash; Update an existing entry</li>
	<li><b>delete &lt;id&gt;</b> &mdash; Delete an entry</li>
	<li><b>exit</b> &mdash; Exit the CLI</li>
</ul>


## 📝 Example

<details>
<summary>Click to expand a sample session</summary>

```bash
> python main.py

Welcome to Mini-Wiki 📚
Choose a command: add / view / search / update / delete / exit

> add

Title: Horus Heresy
Category: Warhammer 40k
Content: The Horus Heresy was a galaxy-spanning civil war in the 31st millennium...
✅ Entry added!

> view

[1] Horus Heresy (Warhammer 40k)

```
</details>


## Future Additions

- **Tags**: Implement a tagging system for entries.
- **Edit History**: Keep track of changes made to entries.
- **Import/Export**: Allow importing/exporting entries from/to other formats (e.g., Markdown).
- **User Accounts**: Implement user accounts and authentication.
- **Cloud Sync**: Option to sync entries with a cloud service.
