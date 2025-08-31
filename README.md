# 🗺️ AtlasMogo

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PySide6](https://img.shields.io/badge/PySide6-6.0+-orange.svg)](https://doc.qt.io/qtforpython/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.0+-green.svg)](https://www.mongodb.com/)

> A modern, professional MongoDB management tool built with Python and PySide6, featuring a clean layered architecture for enterprise-grade database operations.

## 📋 Table of Contents

- [About](#about)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Development](#-development)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

## About

**AtlasMogo** is a desktop application that provides a modern, intuitive interface for managing MongoDB databases. Built with Python and PySide6, it offers enterprise-grade functionality with a clean, professional design.

### Why AtlasMogo?

- **Modern UI**: Clean, responsive interface built with PySide6
- **Layered Architecture**: Clean separation of concerns for maintainability
- **Professional Features**: Comprehensive CRUD operations, logging, and error handling
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Developer-Friendly**: Extensive logging and debugging capabilities

### Architecture

AtlasMogo follows a **Layered Architecture** pattern:

```
┌─────────────────────────────────────┐
│           Presentation Layer        │
│         (PySide6 GUI)               │
├─────────────────────────────────────┤
│         Business Logic Layer        │
│      (Application Services)         │
├─────────────────────────────────────┤
│         Data Access Layer           │
│        (MongoDB Repository)         │
└─────────────────────────────────────┘
```

## ✨ Features

### 🔧 Core Functionality
- **MongoDB CRUD Operations**: Full Create, Read, Update, Delete support
- **Database Navigation**: Browse databases and collections with sidebar
- **Document Management**: View, edit, and manage documents in tabular format
- **Query Execution**: Execute custom MongoDB queries
- **Connection Management**: Support for local and remote MongoDB instances

### 🎨 User Experience
- **Modern GUI**: Clean, intuitive interface with professional styling
- **Context Menus**: Right-click context menus for quick operations
- **Responsive Design**: Adaptive layout for different screen sizes
- **Professional Dialogs**: Confirmation dialogs with proper user flows
- **Real-time Feedback**: Live connection status and operation feedback

### 🛠️ Technical Features
- **Layered Architecture**: Clean separation of concerns
- **Comprehensive Logging**: Detailed logging system for debugging
- **Error Handling**: Robust error handling with user-friendly messages
- **Threading**: Non-blocking UI with background operations
- **Configuration Management**: Centralized settings and configuration
- **Icon Support**: Custom application icon for professional appearance

### 🌐 Cross-Platform Support
- **Windows**: Full support with native executable
- **Linux**: Compatible with major distributions
- **macOS**: Native macOS application support

## 📁 Project Structure

```
AtlasMogo/
├── presentation/              # GUI components (PySide6)
│   ├── windows/              # Main application windows
│   │   └── main_window.py    # Main application window
│   ├── panels/               # UI panels and components
│   │   ├── sidebar.py        # Database navigation sidebar
│   │   ├── data_table.py     # Document display table
│   │   ├── toolbar.py        # Application toolbar
│   │   └── connection_panel.py # Connection configuration
│   ├── dialogs/              # Dialog components
│   │   ├── message_box_helper.py # Message box utilities
│   │   └── dialog_helper.py  # Dialog utilities
│   └── styles/               # UI styling and themes
│       └── styles.py         # Application stylesheets
├── business/                 # Business logic layer
│   └── mongo_service.py      # MongoDB service orchestration
├── data/                     # Data access layer
│   ├── mongo_connection.py   # Connection management
│   └── mongo_repository.py   # CRUD operations
├── config/                   # Configuration and settings
│   ├── settings.py           # Application settings
│   └── logging_config.py     # Logging configuration
├── resources/                # Application resources
│   └── icons/                # Application icons
│       └── icon.ico          # Main application icon
├── logs/                     # Application logs
├── tests/                    # Test suite
├── main.py                   # Application entry point
├── build.py                  # PyInstaller build script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🚀 Installation

### Prerequisites
- **Python 3.10** or higher
- **MongoDB** instance (local or remote)

### Quick Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/nghiaomg/AtlasMogo.git
   cd AtlasMogo
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

### Dependencies

The application requires the following Python packages:
- `PySide6` - Modern Qt-based GUI framework
- `pymongo` - Official MongoDB Python driver
- `qtawesome` - Icon library for PySide6
- `python-dotenv` - Environment variable management

## 📖 Usage

### Getting Started

1. **Launch AtlasMogo**
   ```bash
   python main.py
   ```

2. **Connect to MongoDB**
   - Enter your MongoDB connection string
   - Default: `mongodb://localhost:27017`
   - Click "Connect" button

3. **Browse Databases**
   - Select databases from the left sidebar
   - Expand collections within each database
   - Click on collections to view documents

4. **Perform Operations**
   - **View Documents**: Documents display in tabular format
   - **Insert Documents**: Use the insert dialog
   - **Update Documents**: Right-click and select "Edit"
   - **Delete Documents**: Right-click and select "Delete"
   - **Execute Queries**: Use the query panel for custom operations

### Connection Examples

```bash
# Local MongoDB
mongodb://localhost:27017

# With Authentication
mongodb://username:password@localhost:27017

# MongoDB Atlas
mongodb+srv://username:password@cluster.mongodb.net/

# Custom Configuration
mongodb://host:port/database?options
```

### CRUD Operations

#### Insert Document
   ```json
   {
     "name": "John Doe",
     "email": "john@example.com",
  "age": 30,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Update Document
- **Filter**: `{"email": "john@example.com"}`
- **Update**: `{"age": 31, "updated_at": "2024-01-02T00:00:00Z"}`

#### Delete Document
- **Filter**: `{"email": "john@example.com"}`

#### Query Documents
- **Filter**: `{"age": {"$gte": 25}}`
- **Limit**: 100
- **Sort**: `{"created_at": -1}`

## 🛠️ Development

### Building the Executable

AtlasMogo includes a build script for creating standalone executables:

```bash
# Build executable
python build.py

# Clean build artifacts
python build.py clean
```

The build process:
- Uses PyInstaller for packaging
- Includes custom application icon (`resources/icons/icon.ico`)
- Bundles all resources and dependencies
- Creates a single executable file

### Development Setup

1. **Clone and setup**:
   ```bash
   git clone https://github.com/nghiaomg/AtlasMogo.git
   cd AtlasMogo
   pip install -r requirements.txt
   ```

2. **Run in development mode**:
   ```bash
   python main.py
   ```

3. **Check logs**:
   - Application logs are stored in `logs/atlasmogo.log`
   - Detailed logging for debugging and monitoring

### Code Structure

- **Presentation Layer**: UI components in `presentation/`
- **Business Layer**: Application logic in `business/`
- **Data Layer**: Database operations in `data/`
- **Configuration**: Settings and logging in `config/`

## 🗺️ Roadmap

### Version 1.1 (Planned)
- [ ] **Advanced Query Builder**: Visual query construction interface
- [ ] **Aggregation Pipeline Support**: MongoDB aggregation operations
- [ ] **Data Export/Import**: Support for JSON, CSV, and other formats
- [ ] **Theme Support**: Light/dark theme switching

### Version 1.2 (Planned)
- [ ] **Backup & Restore**: Database backup and restoration tools
- [ ] **Data Migration**: Tools for database migration
- [ ] **Performance Monitoring**: Real-time performance metrics
- [ ] **User Management**: Multi-user support with roles

### Version 2.0 (Future)
- [ ] **Cloud Integration**: Direct MongoDB Atlas integration
- [ ] **Data Visualization**: Charts and graphs for data analysis
- [ ] **Plugin System**: Extensible architecture for custom functionality
- [ ] **Advanced Analytics**: Built-in analytics and reporting

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Getting Started

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes** and add tests
4. **Commit your changes**:
   ```bash
   git commit -m 'Add amazing feature'
   ```
5. **Push to the branch**:
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open a Pull Request**

### Development Guidelines

- Follow **PEP 8** style guidelines
- Add comprehensive **docstrings** to functions and classes
- Write **unit tests** for new features
- Update **documentation** for any changes
- Ensure **error handling** is robust

### Reporting Issues

- Use the GitHub issue tracker
- Provide detailed reproduction steps
- Include system information and error logs
- Check existing issues before creating new ones

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 nghiaomg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👨‍💻 Author

**AtlasMogo** is created and maintained by **nghiaomg**.

- **GitHub**: [github.com/nghiaomg](https://github.com/nghiaomg)
- **Project**: [AtlasMogo Repository](https://github.com/nghiaomg/AtlasMogo)

### Acknowledgments

- **MongoDB Team** - For the excellent database platform
- **Qt/PySide6 Community** - For the powerful GUI framework
- **Python Community** - For the amazing ecosystem and tools

---

<div align="center">

**AtlasMogo** - Empowering MongoDB management with Python excellence! 🐍✨

[![GitHub stars](https://img.shields.io/github/stars/nghiaomg/AtlasMogo?style=social)](https://github.com/nghiaomg/AtlasMogo/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/nghiaomg/AtlasMogo?style=social)](https://github.com/nghiaomg/AtlasMogo/network/members)

*Made with ❤️ by the AtlasMogo community*

</div>
