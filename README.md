
# 📁 Mini-Wiki CLI</h1>
  
A simple command-line wiki that allows you to store, search and manage knowledge entries.

Think of it as a personal offline encyclopedia, perfect for notes, lore, worldbuilding or study material.

[![CLI Tool](https://img.shields.io/badge/CLI-Tool-blue.svg)](https://github.com)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://python.org/)
[![Offline Ready](https://img.shields.io/badge/Offline-Ready-orange.svg)](https://github.com)

---

## ✨ Features

<ul>
	<li><b>➕ Add</b> &mdash; Adds new entries with a title, category and content.</li>
	<li><b>📖 View</b> &mdash; View all entries or filter by category.</li>
	<li><b>🔍 Search</b> &mdash; Search for entries by keyword.</li>
	<li><b>✏️ Update</b> &mdash; Modify existing entries by title.</li>
	<li><b>🗑️ Delete</b> &mdash; Remove entries by title.</li>
	<li><b>📦 Store</b> &mdash; Save all entries to a file.</li>
</ul>



## 📂 Project Structure

```text
mini_wiki/
│── README.md              # project description & usage
│── main.py                # entry point for the CLI
│── db/
│   └── wiki.db            # SQLite database file (auto-created on first run)
│── wiki/
│   │── __init__.py        # makes it a package
│   │── db_handler.py      # database connection, schema setup
│   │── crud.py            # create, read, update, delete functions
│   │── cli.py             # command-line interface (menus, prompts)
│   └── entry.py           # entry data model
└── .gitignore             # ignore db files, pycache, etc.
```


## 🚀 Usage

```bash
# Start the CLI
python main.py
```


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
