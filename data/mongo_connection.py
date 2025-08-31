"""
MongoDB Connection Manager
Handles connection to MongoDB instances and provides connection status.
"""

from typing import Optional, Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging

logger = logging.getLogger(__name__)


class MongoConnection:
    """Manages MongoDB connections and provides connection utilities."""
    
    def __init__(self):
        """Initialize the MongoDB connection manager."""
        self._client: Optional[MongoClient] = None
        self._connection_string: Optional[str] = None
        self._is_connected: bool = False
        self._connection_info: Dict[str, Any] = {}
    
    def connect(self, connection_string: str, timeout_ms: int = 5000) -> bool:
        """
        Connect to MongoDB using the provided connection string.
        
        Args:
            connection_string: MongoDB connection string
            timeout_ms: Connection timeout in milliseconds
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Close existing connection if any
            self.disconnect()
            
            # Create new client
            self._client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=timeout_ms,
                connectTimeoutMS=timeout_ms
            )
            
            # Test connection
            self._client.admin.command('ping')
            
            # Store connection info
            self._connection_string = connection_string
            self._is_connected = True
            
            # Get server info
            server_info = self._client.server_info()
            
            # Extract host and port from connection string or server info
            host = None
            port = None
            
            # Try to get from server info first
            if server_info.get('host'):
                host = server_info.get('host')
            elif server_info.get('me'):
                # 'me' field contains host:port
                me = server_info.get('me', '')
                if ':' in me:
                    host, port_str = me.split(':', 1)
                    try:
                        port = int(port_str)
                    except ValueError:
                        pass
                else:
                    host = me
            
            # Fallback to connection string parsing
            if not host and 'localhost' in connection_string:
                host = 'localhost'
            if not port and '27017' in connection_string:
                port = 27017
            
            self._connection_info = {
                'version': server_info.get('version'),
                'host': host,
                'port': port,
                'max_bson_object_size': server_info.get('maxBsonObjectSize'),
                'max_message_size_bytes': server_info.get('maxMessageSizeBytes'),
                'connection_string': connection_string
            }
            
            logger.info(f"Successfully connected to MongoDB: {self._connection_info}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._is_connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            self._is_connected = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from MongoDB and clean up resources."""
        if self._client:
            try:
                self._client.close()
                logger.info("Disconnected from MongoDB")
            except Exception as e:
                logger.error(f"Error during disconnection: {e}")
            finally:
                self._client = None
                self._is_connected = False
                self._connection_info = {}
    
    def is_connected(self) -> bool:
        """Check if currently connected to MongoDB."""
        return self._is_connected and self._client is not None
    
    def get_client(self) -> Optional[MongoClient]:
        """Get the MongoDB client instance."""
        return self._client if self._is_connected else None
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        return self._connection_info.copy()
    
    def test_connection(self) -> bool:
        """Test if the current connection is still alive."""
        if not self.is_connected():
            return False
        
        try:
            self._client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            self._is_connected = False
            return False
