"""
MongoDB Repository
Handles all CRUD operations and database/collection management.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
import logging
import datetime

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
                      query: Dict[str, Any] = None, limit: int = 100, 
                      skip: int = 0, sort: List[Tuple[str, int]] = None) -> List[Dict[str, Any]]:
        """
        Find documents in a collection with pagination support.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            query: MongoDB query filter
            limit: Maximum number of documents to return
            skip: Number of documents to skip (for pagination)
            sort: List of (field, direction) tuples for sorting (1=asc, -1=desc)
            
        Returns:
            List of documents
        """
        try:
            db = self._client[database_name]
            collection = db[collection_name]
            
            if query is None:
                query = {}
            
            cursor = collection.find(query)
            
            # Apply sorting if specified
            if sort:
                cursor = cursor.sort(sort)
            
            # Apply pagination
            if skip > 0:
                cursor = cursor.skip(skip)
            
            cursor = cursor.limit(limit)
            
            documents = list(cursor)
            logger.debug(f"Retrieved {len(documents)} documents from {collection_name} "
                        f"(skip: {skip}, limit: {limit})")
            
            return documents
        except PyMongoError as e:
            logger.error(f"Error finding documents in {collection_name}: {e}")
            return []
    
    def count_documents(self, database_name: str, collection_name: str, 
                       query: Dict[str, Any] = None) -> int:
        """
        Count documents in a collection efficiently.
        
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
            
            count = collection.count_documents(query)
            logger.debug(f"Collection {collection_name} has {count} documents")
            return count
        except PyMongoError as e:
            logger.error(f"Error counting documents in {collection_name}: {e}")
            return 0
    
    def get_collection_stats(self, database_name: str, collection_name: str) -> Dict[str, Any]:
        """
        Get collection statistics including document count and storage info.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            
        Returns:
            Collection statistics
        """
        try:
            db = self._client[database_name]
            collection = db[collection_name]
            
            stats = db.command("collStats", collection_name)
            logger.debug(f"Retrieved stats for collection {collection_name}")
            return stats
        except PyMongoError as e:
            logger.error(f"Error getting stats for {collection_name}: {e}")
            return {}
    
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
    
    def insert_many(self, database_name: str, collection_name: str, 
                   documents: List[Dict[str, Any]]) -> int:
        """
        Insert multiple documents into a collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            documents: List of documents to insert
            
        Returns:
            Number of documents inserted
        """
        try:
            db = self._client[database_name]
            collection = db[collection_name]
            
            if not documents:
                logger.warning(f"No documents to insert into {collection_name}")
                return 0
            
            result = collection.insert_many(documents)
            logger.info(f"Inserted {len(result.inserted_ids)} documents into {collection_name}")
            return len(result.inserted_ids)
        except PyMongoError as e:
            logger.error(f"Error inserting documents into {collection_name}: {e}")
            return 0
    
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
    
    def replace_document(self, database_name: str, collection_name: str, 
                        document_id, new_document: Dict[str, Any]) -> bool:
        """
        Replace a document in a collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            document_id: The _id of the document to replace
            new_document: New document data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from bson import ObjectId
            
            db = self._client[database_name]
            collection = db[collection_name]
            
            # Convert string _id to ObjectId if needed
            if isinstance(document_id, str):
                try:
                    document_id = ObjectId(document_id)
                except Exception:
                    # If it's not a valid ObjectId, use as string
                    pass
            
            # Preserve the original _id
            new_document["_id"] = document_id
            
            result = collection.replace_one({"_id": document_id}, new_document)
            logger.info(f"Document replaced: {result.modified_count} modified")
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Error replacing document in {collection_name}: {e}")
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
    
    def delete_document_by_id(self, database_name: str, collection_name: str, 
                             document_id) -> bool:
        """
        Delete a document by its _id.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            document_id: The _id of the document to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from bson import ObjectId
            
            db = self._client[database_name]
            collection = db[collection_name]
            
            # Convert string _id to ObjectId if needed
            if isinstance(document_id, str):
                try:
                    document_id = ObjectId(document_id)
                except Exception:
                    # If it's not a valid ObjectId, use as string
                    pass
            
            result = collection.delete_one({"_id": document_id})
            logger.info(f"Document deleted by _id {document_id}: {result.deleted_count} deleted")
            return result.deleted_count > 0
        except PyMongoError as e:
            logger.error(f"Error deleting document with _id {document_id} from {collection_name}: {e}")
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
    
    def rename_collection(self, database_name: str, old_name: str, new_name: str) -> bool:
        """
        Rename a collection using admin database command.
        
        Args:
            database_name: Name of the database
            old_name: Current collection name
            new_name: New collection name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use admin database with fully qualified namespace
            self._client.admin.command(
                "renameCollection",
                f"{database_name}.{old_name}",
                to=f"{database_name}.{new_name}",
                dropTarget=False
            )
            logger.info(f"Collection {database_name}.{old_name} renamed to {database_name}.{new_name} successfully")
            return True
        except PyMongoError as e:
            logger.error(f"Error renaming collection {database_name}.{old_name} to {database_name}.{new_name}: {e}")
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
            # We'll create a persistent collection to ensure the database remains visible
            db = self._client[database_name]
            
            # Create a persistent collection with a document to ensure database visibility
            init_collection = db["__init__"]
            init_collection.insert_one({
                "created_at": datetime.datetime.utcnow(),
                "purpose": "Database initialization",
                "note": "This collection ensures the database remains visible in MongoDB"
            })
            
            # Create an index on the created_at field for better performance
            init_collection.create_index("created_at")
            
            logger.info(f"Database {database_name} created successfully with initialization collection")
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
