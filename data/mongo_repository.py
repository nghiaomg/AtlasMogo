"""
MongoDB Repository
Handles all CRUD operations and database/collection management.
"""

from typing import List, Dict, Any, Optional, Union
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
import logging

logger = logging.getLogger(__name__)


class MongoRepository:
    """Repository class for MongoDB operations."""
    
    def __init__(self, client: MongoClient):
        """
        Initialize the repository with a MongoDB client.
        
        Args:
            client: MongoDB client instance
        """
        self._client = client
    
    def get_databases(self) -> List[str]:
        """
        Get list of all database names.
        
        Returns:
            List of database names
        """
        try:
            return self._client.list_database_names()
        except PyMongoError as e:
            logger.error(f"Error listing databases: {e}")
            return []
    
    def get_collections(self, database_name: str) -> List[str]:
        """
        Get list of collection names in a database.
        
        Args:
            database_name: Name of the database
            
        Returns:
            List of collection names
        """
        try:
            db = self._client[database_name]
            return db.list_collection_names()
        except PyMongoError as e:
            logger.error(f"Error listing collections in {database_name}: {e}")
            return []
    
    def get_database_stats(self, database_name: str) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Args:
            database_name: Name of the database
            
        Returns:
            Database statistics
        """
        try:
            db = self._client[database_name]
            return db.command("dbStats")
        except PyMongoError as e:
            logger.error(f"Error getting stats for {database_name}: {e}")
            return {}
    
    def get_collection_stats(self, database_name: str, collection_name: str) -> Dict[str, Any]:
        """
        Get collection statistics.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            
        Returns:
            Collection statistics
        """
        try:
            db = self._client[database_name]
            collection = db[collection_name]
            return db.command("collStats", collection_name)
        except PyMongoError as e:
            logger.error(f"Error getting stats for {collection_name}: {e}")
            return {}
    
    def find_documents(self, database_name: str, collection_name: str, 
                      query: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Find documents in a collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            query: MongoDB query filter
            limit: Maximum number of documents to return
            
        Returns:
            List of documents
        """
        try:
            db = self._client[database_name]
            collection = db[collection_name]
            
            if query is None:
                query = {}
            
            cursor = collection.find(query).limit(limit)
            return list(cursor)
        except PyMongoError as e:
            logger.error(f"Error finding documents in {collection_name}: {e}")
            return []
    
    def count_documents(self, database_name: str, collection_name: str, 
                       query: Dict[str, Any] = None) -> int:
        """
        Count documents in a collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            query: MongoDB query filter
            
        Returns:
            Number of documents
        """
        try:
            db = self._client[database_name]
            collection = db[collection_name]
            
            if query is None:
                query = {}
            
            return collection.count_documents(query)
        except PyMongoError as e:
            logger.error(f"Error counting documents in {collection_name}: {e}")
            return 0
    
    def insert_document(self, database_name: str, collection_name: str, 
                       document: Dict[str, Any]) -> Optional[str]:
        """
        Insert a single document into a collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            document: Document to insert
            
        Returns:
            Inserted document ID if successful, None otherwise
        """
        try:
            db = self._client[database_name]
            collection = db[collection_name]
            
            result = collection.insert_one(document)
            logger.info(f"Document inserted with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Error inserting document into {collection_name}: {e}")
            return None
    
    def update_document(self, database_name: str, collection_name: str, 
                       filter_query: Dict[str, Any], update_data: Dict[str, Any]) -> bool:
        """
        Update a document in a collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            filter_query: Query to find the document to update
            update_data: Data to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db = self._client[database_name]
            collection = db[collection_name]
            
            result = collection.update_one(filter_query, {"$set": update_data})
            logger.info(f"Document updated: {result.modified_count} modified")
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Error updating document in {collection_name}: {e}")
            return False
    
    def delete_document(self, database_name: str, collection_name: str, 
                       filter_query: Dict[str, Any]) -> bool:
        """
        Delete a document from a collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            filter_query: Query to find the document to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db = self._client[database_name]
            collection = db[collection_name]
            
            result = collection.delete_one(filter_query)
            logger.info(f"Document deleted: {result.deleted_count} deleted")
            return result.deleted_count > 0
        except PyMongoError as e:
            logger.error(f"Error deleting document from {collection_name}: {e}")
            return False
    
    def create_collection(self, database_name: str, collection_name: str) -> bool:
        """
        Create a new collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db = self._client[database_name]
            db.create_collection(collection_name)
            logger.info(f"Collection {collection_name} created successfully")
            return True
        except PyMongoError as e:
            logger.error(f"Error creating collection {collection_name}: {e}")
            return False
    
    def drop_collection(self, database_name: str, collection_name: str) -> bool:
        """
        Drop a collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db = self._client[database_name]
            db[collection_name].drop()
            logger.info(f"Collection {collection_name} dropped successfully")
            return True
        except PyMongoError as e:
            logger.error(f"Error dropping collection {collection_name}: {e}")
            return False
    
    def create_database(self, database_name: str) -> bool:
        """
        Create a new database.
        
        Args:
            database_name: Name of the database
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # MongoDB creates databases when you first insert data
            # We'll create a temporary collection and then drop it
            db = self._client[database_name]
            temp_collection = db["__temp__"]
            temp_collection.insert_one({"created": True})
            temp_collection.drop()
            logger.info(f"Database {database_name} created successfully")
            return True
        except PyMongoError as e:
            logger.error(f"Error creating database {database_name}: {e}")
            return False
    
    def rename_database(self, old_name: str, new_name: str) -> bool:
        """
        Rename a database.
        
        Args:
            old_name: Current database name
            new_name: New database name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # MongoDB doesn't support direct database renaming
            # We need to copy all collections to the new database and drop the old one
            old_db = self._client[old_name]
            new_db = self._client[new_name]
            
            # Get all collections from old database
            collections = old_db.list_collection_names()
            
            # Copy each collection
            for collection_name in collections:
                old_collection = old_db[collection_name]
                new_collection = new_db[collection_name]
                
                # Copy all documents
                documents = old_collection.find({})
                if documents.count() > 0:
                    new_collection.insert_many(documents)
            
            # Drop the old database
            self._client.drop_database(old_name)
            
            logger.info(f"Database {old_name} renamed to {new_name} successfully")
            return True
        except PyMongoError as e:
            logger.error(f"Error renaming database {old_name} to {new_name}: {e}")
            return False
    
    def delete_database(self, database_name: str) -> bool:
        """
        Delete a database.
        
        Args:
            database_name: Name of the database
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._client.drop_database(database_name)
            logger.info(f"Database {database_name} deleted successfully")
            return True
        except PyMongoError as e:
            logger.error(f"Error deleting database {database_name}: {e}")
            return False
