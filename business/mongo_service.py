"""
MongoDB Service
Business logic layer for MongoDB operations and data orchestration.
"""

from typing import List, Dict, Any, Optional, Tuple
from data.mongo_connection import MongoConnection
from data.mongo_repository import MongoRepository
import logging

logger = logging.getLogger(__name__)


class MongoService:
    """Service class that orchestrates MongoDB operations."""
    
    def __init__(self):
        """Initialize the MongoDB service."""
        self._connection = MongoConnection()
        self._repository: Optional[MongoRepository] = None
    
    def connect_to_mongodb(self, connection_string: str) -> Tuple[bool, str]:
        """
        Connect to MongoDB and initialize repository.
        
        Args:
            connection_string: MongoDB connection string
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if self._connection.connect(connection_string):
                client = self._connection.get_client()
                if client:
                    self._repository = MongoRepository(client)
                    return True, "Connected successfully to MongoDB"
                else:
                    return False, "Failed to get MongoDB client"
            else:
                return False, "Failed to connect to MongoDB"
        except Exception as e:
            logger.error(f"Error in connect_to_mongodb: {e}")
            return False, f"Connection error: {str(e)}"
    
    def disconnect_from_mongodb(self) -> None:
        """Disconnect from MongoDB and clean up."""
        self._connection.disconnect()
        self._repository = None
    
    def is_connected(self) -> bool:
        """Check if connected to MongoDB."""
        return self._connection.is_connected()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get MongoDB connection information."""
        return self._connection.get_connection_info()
    
    def get_databases(self) -> List[str]:
        """
        Get list of databases.
        
        Returns:
            List of database names
        """
        if not self._repository:
            return []
        
        try:
            return self._repository.get_databases()
        except Exception as e:
            logger.error(f"Error getting databases: {e}")
            return []
    
    def get_collections(self, database_name: str) -> List[str]:
        """
        Get list of collections in a database.
        
        Returns:
            List of collection names
        """
        if not self._repository:
            return []
        
        try:
            return self._repository.get_collections(database_name)
        except Exception as e:
            logger.error(f"Error getting collections: {e}")
            return []
    
    def get_database_stats(self, database_name: str) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Database statistics
        """
        if not self._repository:
            return {}
        
        try:
            return self._repository.get_database_stats(database_name)
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def get_collection_stats(self, database_name: str, collection_name: str) -> Dict[str, Any]:
        """
        Get collection statistics.
        
        Returns:
            Collection statistics
        """
        if not self._repository:
            return {}
        
        try:
            return self._repository.get_collection_stats(database_name, collection_name)
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    def get_collection_info(self, database_name: str, collection_name: str) -> Dict[str, Any]:
        """
        Get comprehensive collection information including count and stats.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            
        Returns:
            Collection information with count and stats
        """
        if not self._repository:
            return {"count": 0, "stats": {}}
        
        try:
            count = self._repository.count_documents(database_name, collection_name)
            stats = self._repository.get_collection_stats(database_name, collection_name)
            
            return {
                "count": count,
                "stats": stats,
                "estimated_size_mb": stats.get("size", 0) / (1024 * 1024) if stats else 0
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {"count": 0, "stats": {}}
    
    def find_documents(self, database_name: str, collection_name: str, 
                      query: str = None, limit: int = 100, 
                      skip: int = 0, sort: List[Tuple[str, int]] = None) -> List[Dict[str, Any]]:
        """
        Find documents in a collection with pagination support.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            query: JSON string query filter
            limit: Maximum number of documents
            skip: Number of documents to skip (for pagination)
            sort: List of (field, direction) tuples for sorting (1=asc, -1=desc)
            
        Returns:
            List of documents
        """
        if not self._repository:
            return []
        
        try:
            # Parse query string to dict if provided
            query_dict = None
            if query and query.strip():
                import json
                query_dict = json.loads(query)
            
            return self._repository.find_documents(
                database_name, collection_name, query_dict, limit, skip, sort
            )
        except json.JSONDecodeError:
            logger.error("Invalid JSON query format")
            return []
        except Exception as e:
            logger.error(f"Error finding documents: {e}")
            return []
    
    def count_documents(self, database_name: str, collection_name: str, 
                       query: str = None) -> int:
        """
        Count documents in a collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            query: JSON string query filter
            
        Returns:
            Number of documents
        """
        if not self._repository:
            return 0
        
        try:
            # Parse query string to dict if provided
            query_dict = None
            if query and query.strip():
                import json
                query_dict = json.loads(query)
            
            return self._repository.count_documents(database_name, collection_name, query_dict)
        except json.JSONDecodeError:
            logger.error("Invalid JSON query format")
            return 0
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            return 0
    
    def insert_document(self, database_name: str, collection_name: str, 
                       document: str) -> Tuple[bool, str]:
        """
        Insert a document into a collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            document: JSON string document
            
        Returns:
            Tuple of (success, message)
        """
        if not self._repository:
            return False, "Not connected to MongoDB"
        
        try:
            # Parse document string to dict
            import json
            document_dict = json.loads(document)
            
            doc_id = self._repository.insert_document(database_name, collection_name, document_dict)
            if doc_id:
                return True, f"Document inserted with ID: {doc_id}"
            else:
                return False, "Failed to insert document"
        except json.JSONDecodeError:
            return False, "Invalid JSON document format"
        except Exception as e:
            logger.error(f"Error inserting document: {e}")
            return False, f"Insert error: {str(e)}"
    
    def update_document(self, database_name: str, collection_name: str, 
                       filter_query: str, update_data: str) -> Tuple[bool, str]:
        """
        Update a document in a collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            filter_query: JSON string filter query
            update_data: JSON string update data
            
        Returns:
            Tuple of (success, message)
        """
        if not self._repository:
            return False, "Not connected to MongoDB"
        
        try:
            # Parse JSON strings to dicts
            import json
            filter_dict = json.loads(filter_query)
            update_dict = json.loads(update_data)
            
            success = self._repository.update_document(database_name, collection_name, filter_dict, update_dict)
            if success:
                return True, "Document updated successfully"
            else:
                return False, "No documents matched the filter"
        except json.JSONDecodeError:
            return False, "Invalid JSON format in filter or update data"
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return False, f"Update error: {str(e)}"
    
    def delete_document(self, database_name: str, collection_name: str, 
                       filter_query: str) -> Tuple[bool, str]:
        """
        Delete a document from a collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            filter_query: JSON string filter query
            
        Returns:
            Tuple of (success, message)
        """
        if not self._repository:
            return False, "Not connected to MongoDB"
        
        try:
            # Parse filter query string to dict
            import json
            filter_dict = json.loads(filter_query)
            
            success = self._repository.delete_document(database_name, collection_name, filter_dict)
            if success:
                return True, "Document deleted successfully"
            else:
                return False, "No documents matched the filter"
        except json.JSONDecodeError:
            return False, "Invalid JSON format in filter query"
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False, f"Delete error: {str(e)}"
    
    def delete_document_by_id(self, database_name: str, collection_name: str, 
                             document_id) -> Tuple[bool, str]:
        """
        Delete a document by its _id.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            document_id: The _id of the document to delete
            
        Returns:
            Tuple of (success, message)
        """
        if not self._repository:
            return False, "Not connected to MongoDB"
        
        try:
            logger.info(f"Attempting to delete document with _id: {document_id}")
            success = self._repository.delete_document_by_id(database_name, collection_name, document_id)
            if success:
                logger.info(f"Successfully deleted document with _id: {document_id}")
                return True, f"Document with _id {document_id} deleted successfully"
            else:
                logger.warning(f"No document found with _id: {document_id}")
                return False, f"No document found with _id {document_id}"
        except Exception as e:
            logger.error(f"Error deleting document with _id {document_id}: {e}", exc_info=True)
            return False, f"Delete error: {str(e)}"
    
    def create_collection(self, database_name: str, collection_name: str) -> Tuple[bool, str]:
        """
        Create a new collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            
        Returns:
            Tuple of (success, message)
        """
        if not self._repository:
            return False, "Not connected to MongoDB"
        
        try:
            success = self._repository.create_collection(database_name, collection_name)
            if success:
                return True, f"Collection '{collection_name}' created successfully"
            else:
                return False, f"Failed to create collection '{collection_name}'"
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return False, f"Create collection error: {str(e)}"
    
    def drop_collection(self, database_name: str, collection_name: str) -> Tuple[bool, str]:
        """
        Drop a collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            
        Returns:
            Tuple of (success, message)
        """
        if not self._repository:
            return False, "Not connected to MongoDB"
        
        try:
            success = self._repository.drop_collection(database_name, collection_name)
            if success:
                return True, f"Collection '{collection_name}' dropped successfully"
            else:
                return False, f"Failed to drop collection '{collection_name}'"
        except Exception as e:
            logger.error(f"Error dropping collection: {e}")
            return False, f"Drop collection error: {str(e)}"
    
    def create_database(self, database_name: str) -> Tuple[bool, str]:
        """
        Create a new database.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Tuple of (success, message)
        """
        if not self._repository:
            return False, "Not connected to MongoDB"
        
        try:
            success = self._repository.create_database(database_name)
            if success:
                return True, f"Database '{database_name}' created successfully"
            else:
                return False, f"Failed to create database '{database_name}'"
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            return False, f"Create database error: {str(e)}"
    
    def rename_database(self, old_name: str, new_name: str) -> Tuple[bool, str]:
        """
        Rename a database.
        
        Args:
            old_name: Current database name
            new_name: New database name
            
        Returns:
            Tuple of (success, message)
        """
        if not self._repository:
            return False, "Not connected to MongoDB"
        
        try:
            success = self._repository.rename_database(old_name, new_name)
            if success:
                return True, f"Database '{old_name}' renamed to '{new_name}' successfully"
            else:
                return False, f"Failed to rename database '{old_name}' to '{new_name}'"
        except Exception as e:
            logger.error(f"Error renaming database: {e}")
            return False, f"Rename database error: {str(e)}"
    
    def delete_database(self, database_name: str) -> Tuple[bool, str]:
        """
        Delete a database.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Tuple of (success, message)
        """
        if not self._repository:
            return False, "Not connected to MongoDB"
        
        try:
            success = self._repository.delete_database(database_name)
            if success:
                return True, f"Database '{database_name}' deleted successfully"
            else:
                return False, f"Failed to delete database '{database_name}'"
        except Exception as e:
            logger.error(f"Error deleting database: {e}")
            return False, f"Delete database error: {str(e)}"
