# AtlasMogo v1.1

[![Version](https://img.shields.io/badge/version-v1.1-blue.svg)](https://github.com/nghiaomg/AtlasMogo/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![PySide6](https://img.shields.io/badge/PySide6-6.0+-blue.svg)](https://doc.qt.io/qtforpython/)

<div align="center">
  <img src="resources/icons/logo.png" alt="AtlasMogo Logo" width="120" height="120">
  <h3>A lightweight and user-friendly MongoDB GUI client built with Python and PySide6</h3>
</div>

---

## 📖 Overview

AtlasMogo is a modern, intuitive MongoDB management tool that provides a clean interface for database operations. Built with Python and PySide6, it offers both table and JSON views for document management, making it perfect for developers and database administrators who prefer a lightweight alternative to heavy database clients.

## 🖼️ Screenshots

<div align="center">
  <img src="https://i.ibb.co/kbz5ySY/Screenshot-2025-08-31-171807.png" alt="AtlasMogo Main Interface" width="800">
  <p><em>Main interface showing Table View with document management capabilities</em></p>
</div>

## ✨ Features

- **🔌 Easy MongoDB Connection**
  - Simple connection dialog with host, port, and authentication
  - Support for connection strings and individual parameters
  - Connection status indicators

- **📊 Dual Document Views**
  - **Table View**: phpMyAdmin-like interface for easy data scanning
  - **Object View**: JSON editor with syntax highlighting and real-time validation

- **✏️ Advanced Document Editing**
  - Inline JSON editing with auto-formatting
  - Real-time validation with error highlighting and tooltips
  - Save/Cancel functionality with toast notifications
  - Support for MongoDB-specific data types (ObjectId, Date, etc.)

- **🗂️ Collection Management**
  - Create, rename, and delete collections
  - View collection statistics and document counts
  - Refresh and reload operations

- **🧹 Bulk Delete Documents (New)**
  - Delete multiple documents at once in both Table View and JSON/Object View
  - Confirmation dialog and toast feedback

- **📤 Export Database (New)**
  - Export entire database (all collections + documents)
  - Formats: JSON (per-collection files), BSON, optional ZIP compression

- **📥 Import Database (New)**
  - Import from JSON/BSON/ZIP or a directory with per-collection files
  - Per-collection overwrite prompts with progress feedback

- **📘 Export Schema (New)**
  - Export database schema (all collections) to JSON / YAML / Markdown
  - Markdown output includes TOC, field summaries, and formatted code blocks

- **🎨 Professional UI/UX**
  - Intuitive dialogs with styled buttons (Save/Cancel, Yes/No)
  - Consistent design language throughout the application
  - Responsive layout with proper loading indicators
  - Toast notifications for user feedback

- **📝 Comprehensive Logging**
  - Detailed logging for all major operations
  - Debug information for troubleshooting
  - User action tracking

## 🚀 Installation

### Windows Users (Recommended)
1. **Download the Release**: Go to [GitHub Releases](https://github.com/nghiaomg/AtlasMogo/releases)
2. **Download**: Click on `AtlasMogo-v1.1.exe` under Assets
3. **Run**: Double-click the `.exe` file - no installation required!

### From Source
```bash
git clone https://github.com/nghiaomg/AtlasMogo.git
cd AtlasMogo
pip install -r requirements.txt
python main.py
```

## 💻 Usage

### Connecting to MongoDB
1. Launch AtlasMogo
2. Click **New Connection** or **Open Connection**
3. Enter your MongoDB connection details:
   - **Host**: `localhost` (default) or your MongoDB server
   - **Port**: `27017` (default) or your custom port
   - **Database**: Your database name
   - **Username/Password**: If authentication is required
4. Click **Connect**

### Managing Documents
1. **Select a Collection**: Choose from the left sidebar
2. **Switch Views**: Use the toggle buttons to switch between Table View and Object View
3. **Edit Documents**:
   - **Table View**: Click on cells to edit values
   - **Object View**: Edit JSON directly with real-time validation
4. **Save Changes**: Click the green **Save** button or **Cancel** to discard

### Bulk Delete Documents (New)
- **Table View**: Select multiple rows → right-click or toolbar → **Delete Selected** → Confirm.
- **Object View (JSON)**: Select multiple document blocks → **Delete Selected** → Confirm.
- A toast will show: “Successfully deleted X documents”.

### Export / Import Database (New)
- **Export Database**: File → **Export Database** → choose format (JSON/BSON) and optional ZIP → choose destination.
- **Import Database**: File → **Import Database** → pick JSON/BSON/ZIP or directory → choose per-collection overwrite → import with progress.

### Export Schema (New)
- Tools → **Export Schema** → pick format (JSON/YAML/Markdown) → save.
- Markdown includes overview, field tables, and a formatted schema block per collection.

### Collection Operations
- **Create Collection**: Right-click on a database → **Create Collection**
- **Rename Collection**: Right-click on collection → **Rename**
- **Delete Collection**: Right-click on collection → **Delete** (with confirmation)

## 🔄 Changelog v1.1

### ✨ New Features
- **Enhanced Object View**: Always-visible JSON editor with auto-formatting
- **Real-time Validation**: JSON syntax validation with error highlighting and tooltips
- **Inline Editing**: Direct JSON editing without expand/collapse mechanisms
- **Toast Notifications**: Success/error feedback for user actions
- **Bulk Delete Documents**: Multi-select delete in Table and JSON/Object views
- **Export Database**: Full database export (JSON/BSON, optional ZIP)
- **Import Database**: Restore from JSON/BSON/ZIP with overwrite prompts
- **Export Schema**: Output database schema to JSON/YAML/Markdown

### 🐛 Bug Fixes
- **Dialog System**: Fixed Save/Cancel, Yes/No buttons functionality
- **Performance**: Resolved JSON validation recursion and app lag issues
- **UI Consistency**: Improved toggle button states and icon visibility

### 🎨 UI/UX Improvements
- **Table View**: Simplified to phpMyAdmin-style layout for better usability
- **Document Display**: Cleaner document cards with consistent styling
- **Button States**: Proper active/inactive visual feedback
- **Loading Indicators**: Better loading state management

### 🔧 Technical Improvements
- **Debounced Validation**: 500ms delay for smooth JSON editing experience
- **Memory Management**: Proper cleanup of validation timers
- **Error Handling**: Graceful degradation and user-friendly error messages
- **Logging**: Reduced spam and better error tracking

## 🚧 Future Improvements

- **Customization Options**: Themes, layouts, and preferences
- **Query Builder**: Visual query construction interface
- **Performance**: Lazy loading for large collections
- **Plugins**: Extension system for custom functionality

## 🛠️ Technical Details

- **Framework**: PySide6 (Qt for Python)
- **Language**: Python 3.8+
- **Database**: MongoDB (pymongo driver)
- **Architecture**: Layered design (Presentation, Business, Data)
- **Platform**: Cross-platform (Windows, macOS, Linux)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/nghiaomg/AtlasMogo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/nghiaomg/AtlasMogo/discussions)
- **Wiki**: [Project Wiki](https://github.com/nghiaomg/AtlasMogo/wiki)

---

<div align="center">
  <p><strong>Project by nghiaomg</strong> — <a href="https://github.com/nghiaomg">GitHub</a></p>
  <p>Made with ❤️ for the MongoDB community</p>
</div>
