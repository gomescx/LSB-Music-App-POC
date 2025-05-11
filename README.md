
# Nenel Music App – POC

A lightweight local web app to help Biodanza teachers assemble, preview, and manage music sessions using Nenel's card system and a local music catalogue.

## 🧰 Tech Stack

- [Python 3.11+](https://www.python.org/downloads/)
- [uv](https://github.com/astral-sh/uv) (for dependency and environment management)
- [Streamlit](https://streamlit.io/)
- [python-docx](https://python-docx.readthedocs.io/)
- [pandas](https://pandas.pydata.org/)

## 🧱 Project Setup

This project uses `uv` to manage dependencies. No `venv`, `requirements.txt`, or `pip` needed.

### 📦 1. Clone the Repository

```bash
git clone "https://dev.azure.com/BiodanzaAustralia/_git/Nenel%20Cards%20Music%20App"
cd "Nenel Cards Music App"

````

### 🧪 2. Initialize the Environment

```bash
uv venv
uv pip install -r requirements.txt  # Optional: if you include fallback reqs file
```

Or simply install dependencies directly:

```bash
uv pip install streamlit pandas python-docx openpyxl
```

### 🏗️ 3. Initialize the Database

```bash
uv run python app/scripts/init_database.py
```

### 🚀 4. Run the App Locally

```bash
uv run streamlit run app/main.py
```

> The app will start in your browser (localhost:8501). Recommend using Firefox.

## 📁 Folder Structure

```
nenel-music-app/
│
├── app/
│   ├── main.py            # Streamlit entry point
│   ├── data_loader.py     # Functions to load Excel data into SQLite database
│   ├── ui.py              # Layout logic for song selection & previews
│   ├── persistence.py     # Save/load session logic
│   ├── exporter.py        # DOCX and playlist file generation
│   ├── db/                # Database module
│   │   ├── __init__.py    
│   │   ├── schema.py      # Database schema definition
│   │   └── queries.py     # Database query functions
│   └── scripts/           # Utility scripts
│       ├── init_database.py     # Initialize database from Excel
│       ├── check_database.py    # Check database contents
│       └── examine_excel.py     # Examine Excel structure
│
├── data/                  # SQLite database storage
├── docs/                  # Documentation
├── input/                 # Input data files
│   └── LSB_Base_flatfile.xlsx  # Source Excel file
├── music_files/           # Local folder with .mp3 or .m4a song files
├── sessions/              # Where saved session JSON files go
├── exports/               # Output directory for DOCX and playlists
└── README.md
```

## 🧪 Development Tips

* Use `uv pip install <package>` to add new dependencies.
* Use `uv run` before any script/Streamlit call to ensure env consistency.
* Prefer relative file paths and keep `music_files/` in project root.
* If using `.env` or config files, don't forget to `.gitignore` them.

## 📚 Roadmap

Planned features:

* ✅ Exercise/song filtering based on Nenel cards
* ✅ In-app audio preview and song selection
* ✅ Session saving and reloading
* 🔜 Session export to Word and playlist files
* 🔜 Song flow analysis / transition preview

