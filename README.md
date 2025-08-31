# AtlasMogo

A professional MongoDB management tool built with Python and PySide6, featuring a clean layered architecture for enterprise-grade database management.

## 🚀 Features

### Core Functionality
- **Database Management**: Connect to local and remote MongoDB instances
- **Collection Operations**: Browse, create, and manage collections
- **CRUD Operations**: Full Create, Read, Update, Delete document support
- **Query Execution**: Advanced query building and execution
- **Real-time Monitoring**: Live connection status and database statistics

### User Experience
- **Modern GUI**: Clean, intuitive interface built with PySide6
- **Responsive Design**: Adaptive layout for different screen sizes
- **Professional Styling**: Material Design-inspired color scheme
- **Keyboard Shortcuts**: Efficient navigation and operation shortcuts

### Technical Features
- **Layered Architecture**: Clean separation of concerns
- **Error Handling**: Comprehensive error handling and user feedback
- **Logging**: Detailed logging for debugging and monitoring
- **Threading**: Non-blocking UI with background operations
- **Extensible Design**: Ready for future feature additions

## 🏗️ Architecture

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

### Layer Responsibilities

- **Presentation Layer**: User interface components and event handling
- **Business Logic Layer**: Application logic, data orchestration, and validation
- **Data Access Layer**: MongoDB connection management and CRUD operations

## 🛠️ Technology Stack

- **Python 3.10+**: Core application language
- **PySide6**: Modern Qt-based GUI framework
- **pymongo**: Official MongoDB Python driver
- **dnspython**: DNS toolkit for MongoDB connection strings
- **python-dotenv**: Environment variable management

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- MongoDB instance (local or remote)

### Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/AtlasMogo.git
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

## 🚀 Quick Start

1. **Launch AtlasMogo**
2. **Connect to MongoDB**:
   - Enter connection string (default: `mongodb://localhost:27017`)
   - Click "Connect"
3. **Browse Databases**: Select databases and collections from the left panel
4. **View Documents**: Click on collections to view documents in tabular format
5. **Perform Operations**: Use the Operations tab for CRUD operations
6. **Execute Queries**: Use the Query tab for custom MongoDB queries

## 📁 Project Structure

```
AtlasMogo/
├── presentation/          # GUI components (PySide6)
│   ├── __init__.py
│   └── main_window.py    # Main application window
├── business/              # Business logic layer
│   ├── __init__.py
│   └── mongo_service.py  # MongoDB service orchestration
├── data/                  # Data access layer
│   ├── __init__.py
│   ├── mongo_connection.py # Connection management
│   └── mongo_repository.py # CRUD operations
├── config/                # Configuration and settings
│   ├── __init__.py
│   ├── settings.py        # Application settings
│   └── logging_config.py  # Logging configuration
├── logs/                  # Application logs
├── tests/                 # Test suite
│   ├── __init__.py
│   └── README.md          # Testing documentation
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🔧 Configuration

### Connection Strings

- **Local MongoDB**: `mongodb://localhost:27017`
- **With Authentication**: `mongodb://username:password@localhost:27017`
- **MongoDB Atlas**: `mongodb+srv://username:password@cluster.mongodb.net/`
- **Custom**: Any valid MongoDB connection string

### Environment Variables

Set environment variables for custom configurations:
```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_TIMEOUT=5000
MONGODB_SERVER_SELECTION_TIMEOUT=3000

# Application Settings
WINDOW_WIDTH=1200
WINDOW_HEIGHT=800
LOG_LEVEL=INFO
```

### Configuration Files

Configuration is centralized in the `config/` directory:
- **`settings.py`**: Application settings, window dimensions, MongoDB defaults
- **`logging_config.py`**: Logging setup and configuration

## 📊 Usage Examples

### Basic CRUD Operations

1. **Insert Document**:
   ```json
   {
     "name": "John Doe",
     "email": "john@example.com",
     "age": 30
   }
   ```

2. **Update Document**:
   - Filter: `{"email": "john@example.com"}`
   - Update: `{"age": 31}`

3. **Delete Document**:
   - Filter: `{"email": "john@example.com"}`

4. **Query Documents**:
   - Filter: `{"age": {"$gte": 25}}`
   - Limit: 100

## 🎨 Customization

### Themes
AtlasMogo supports multiple themes:
- **Default**: Light theme with blue accents
- **Dark**: Dark theme for reduced eye strain

### Styling
Customize the application appearance by modifying the CSS-like styles in `main_window.py`.

## 🧪 Testing

Run the application and test with your MongoDB instance:

1. **Local Testing**: Use MongoDB Community Edition
2. **Remote Testing**: Connect to MongoDB Atlas or other cloud providers
3. **Performance Testing**: Test with large datasets and complex queries

## 🚧 Development

### Adding New Features

1. **Data Layer**: Extend `MongoRepository` for new operations
2. **Business Layer**: Add services in `MongoService`
3. **Presentation Layer**: Create new UI components in `presentation/`

### Code Style
- Follow PEP 8 guidelines
- Add comprehensive docstrings
- Implement proper error handling
- Write unit tests for new features

## 📈 Future Enhancements

### Planned Features
- **Backup & Restore**: Database backup and restoration tools
- **Data Visualization**: Charts and graphs for data analysis
- **User Management**: Multi-user support with role-based access
- **Performance Monitoring**: Real-time performance metrics
- **Export/Import**: Data export in multiple formats
- **Plugin System**: Extensible architecture for custom functionality

### Roadmap
- **v1.1**: Advanced query builder and aggregation pipeline support
- **v1.2**: Backup/restore functionality and data migration tools
- **v1.3**: Performance monitoring and optimization suggestions
- **v2.0**: Multi-database support and advanced analytics

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Getting Help
- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join community discussions for help and ideas

### Common Issues
- **Connection Failed**: Verify MongoDB is running and accessible
- **Authentication Error**: Check username/password in connection string
- **Permission Denied**: Ensure user has appropriate database permissions

## 🙏 Acknowledgments

- **MongoDB Team**: For the excellent database platform
- **Qt/PySide6 Community**: For the powerful GUI framework
- **Python Community**: For the amazing ecosystem and tools

---

**AtlasMogo** - Empowering MongoDB management with Python excellence! 🐍✨
