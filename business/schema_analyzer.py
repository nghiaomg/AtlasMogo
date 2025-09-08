"""
Schema Analyzer Service
Analyzes MongoDB collections to extract field schemas and provide suggestions for filtering.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set
from collections import defaultdict, Counter

from bson import ObjectId
from .mongo_service import MongoService


class SchemaAnalyzer:
    """Analyzes MongoDB collection schemas for filtering suggestions."""
    
    def __init__(self, mongo_service: MongoService):
        self.mongo_service = mongo_service
        self.logger = logging.getLogger(__name__)
        
        # Cache for schema analysis results
        self._schema_cache: Dict[str, Dict[str, Any]] = {}
        self._field_values_cache: Dict[str, Dict[str, List[str]]] = {}
        self._field_types_cache: Dict[str, Dict[str, str]] = {}
        
    def analyze_collection_schema(self, database_name: str, collection_name: str, 
                                sample_size: int = 100) -> Dict[str, Any]:
        """
        Analyze the schema of a collection to extract field information.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            sample_size: Number of documents to sample for analysis
            
        Returns:
            Dictionary containing schema analysis results
        """
        cache_key = f"{database_name}.{collection_name}"
        
        # Return cached result if available
        if cache_key in self._schema_cache:
            self.logger.debug(f"Returning cached schema for {cache_key}")
            return self._schema_cache[cache_key]
        
        try:
            self.logger.info(f"Analyzing schema for collection {cache_key} (sample size: {sample_size})")
            
            # Get sample documents
            documents = self.mongo_service.find_documents(
                database_name, collection_name, "", sample_size
            )
            
            if not documents:
                self.logger.warning(f"No documents found in collection {cache_key}")
                return self._create_empty_schema()
            
            # Analyze schema
            schema = self._analyze_documents(documents)
            
            # Cache the result
            self._schema_cache[cache_key] = schema
            self.logger.info(f"Schema analysis completed for {cache_key}: {len(schema.get('fields', []))} fields found")
            
            return schema
            
        except Exception as e:
            self.logger.error(f"Error analyzing schema for {cache_key}: {e}")
            return self._create_empty_schema()
    
    def _analyze_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a list of documents to extract schema information."""
        field_types = defaultdict(set)
        field_values = defaultdict(Counter)
        field_presence = defaultdict(int)
        total_docs = len(documents)
        
        for doc in documents:
            self._analyze_document(doc, field_types, field_values, field_presence)
        
        # Process results
        schema = {
            'total_documents': total_docs,
            'fields': [],
            'field_stats': {}
        }
        
        for field_name in field_types:
            field_type = self._determine_field_type(field_types[field_name])
            presence_rate = field_presence[field_name] / total_docs
            
            # Get most common values for this field
            common_values = field_values[field_name].most_common(10)
            value_suggestions = [str(val) for val, _ in common_values if val is not None]
            
            field_info = {
                'name': field_name,
                'type': field_type,
                'presence_rate': presence_rate,
                'value_suggestions': value_suggestions,
                'unique_values': len(field_values[field_name])
            }
            
            schema['fields'].append(field_info)
            schema['field_stats'][field_name] = field_info
        
        # Sort fields by presence rate (most common first)
        schema['fields'].sort(key=lambda x: x['presence_rate'], reverse=True)
        
        return schema
    
    def _analyze_document(self, doc: Dict[str, Any], field_types: Dict[str, Set], 
                          field_values: Dict[str, Counter], field_presence: Dict[str, int],
                          prefix: str = "") -> None:
        """Recursively analyze a document to extract field information."""
        for key, value in doc.items():
            field_path = f"{prefix}.{key}" if prefix else key
            
            # Record field presence
            field_presence[field_path] += 1
            
            # Record field type
            field_types[field_path].add(type(value).__name__)
            
            # Record field value (for primitive types)
            if self._is_primitive_value(value):
                field_values[field_path][value] += 1
            
            # Recursively analyze nested objects and arrays
            if isinstance(value, dict):
                self._analyze_document(value, field_types, field_values, field_presence, field_path)
            elif isinstance(value, list) and value:
                # Analyze first few items in arrays
                for i, item in enumerate(value[:5]):  # Limit to first 5 items
                    if isinstance(item, dict):
                        self._analyze_document(item, field_types, field_values, field_presence, f"{field_path}[{i}]")
                    elif self._is_primitive_value(item):
                        field_values[f"{field_path}[item]"][item] += 1
    
    def _is_primitive_value(self, value: Any) -> bool:
        """Check if a value is a primitive type suitable for value suggestions."""
        return isinstance(value, (str, int, float, bool)) and value is not None
    
    def _determine_field_type(self, types: Set[str]) -> str:
        """Determine the primary type of a field from multiple observed types."""
        type_priority = ['ObjectId', 'datetime', 'date', 'int', 'float', 'bool', 'str', 'list', 'dict']
        
        for priority_type in type_priority:
            if priority_type in types:
                return priority_type
        
        # Return the first type if no priority type found
        return list(types)[0] if types else 'unknown'
    
    def _create_empty_schema(self) -> Dict[str, Any]:
        """Create an empty schema result."""
        return {
            'total_documents': 0,
            'fields': [],
            'field_stats': {}
        }
    
    def get_field_names(self, database_name: str, collection_name: str) -> List[str]:
        """Get list of field names for a collection."""
        schema = self.analyze_collection_schema(database_name, collection_name)
        return [field['name'] for field in schema.get('fields', [])]
    
    def get_field_values(self, database_name: str, collection_name: str, 
                        field_name: str, limit: int = 20) -> List[str]:
        """Get common values for a specific field."""
        cache_key = f"{database_name}.{collection_name}"
        
        if cache_key not in self._field_values_cache:
            # Initialize cache
            self._field_values_cache[cache_key] = {}
        
        if field_name not in self._field_values_cache[cache_key]:
            # Get values for this field
            try:
                # Use aggregation to get distinct values
                pipeline = [
                    {"$match": {field_name: {"$exists": True, "$ne": None}}},
                    {"$group": {"_id": f"${field_name}", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": limit}
                ]
                
                # Note: This would require adding aggregation support to MongoService
                # For now, we'll use the schema analysis cache
                schema = self.analyze_collection_schema(database_name, collection_name)
                field_info = schema.get('field_stats', {}).get(field_name, {})
                values = field_info.get('value_suggestions', [])
                
                self._field_values_cache[cache_key][field_name] = values
                
            except Exception as e:
                self.logger.warning(f"Could not get values for field {field_name}: {e}")
                self._field_values_cache[cache_key][field_name] = []
        
        return self._field_values_cache[cache_key].get(field_name, [])
    
    def get_field_type(self, database_name: str, collection_name: str, field_name: str) -> str:
        """Get the type of a specific field."""
        schema = self.analyze_collection_schema(database_name, collection_name)
        field_info = schema.get('field_stats', {}).get(field_name, {})
        return field_info.get('type', 'unknown')
    
    def clear_cache(self, database_name: Optional[str] = None, collection_name: Optional[str] = None):
        """Clear schema analysis cache."""
        if database_name and collection_name:
            cache_key = f"{database_name}.{collection_name}"
            if cache_key in self._schema_cache:
                del self._schema_cache[cache_key]
            if cache_key in self._field_values_cache:
                del self._field_values_cache[cache_key]
            self.logger.debug(f"Cleared cache for {cache_key}")
        else:
            # Clear all cache
            self._schema_cache.clear()
            self._field_values_cache.clear()
            self.logger.debug("Cleared all schema cache")
    
    def analyze_database_schema(self, database_name: str, sample_size: int = 100) -> Dict[str, Dict[str, Any]]:
        """
        Analyze the schema of all collections in a database.
        
        Args:
            database_name: Name of the database
            sample_size: Number of documents to sample per collection
            
        Returns:
            Dictionary mapping collection names to their schema structures
        """
        try:
            self.logger.info(f"Analyzing database schema for {database_name}")
            
            # Get all collections in the database
            collections = self.mongo_service.get_collections(database_name)
            
            if not collections:
                self.logger.warning(f"No collections found in database {database_name}")
                return {}
            
            database_schema = {}
            
            for collection_name in collections:
                try:
                    self.logger.debug(f"Analyzing collection {collection_name}")
                    
                    # Get sample documents
                    documents = self.mongo_service.find_documents(
                        database_name, collection_name, "", sample_size
                    )
                    
                    if not documents:
                        self.logger.debug(f"No documents in collection {collection_name}")
                        database_schema[collection_name] = {}
                        continue
                    
                    # Analyze and convert to simplified schema format
                    collection_schema = self._convert_to_export_schema(documents)
                    database_schema[collection_name] = collection_schema
                    
                except Exception as e:
                    self.logger.error(f"Error analyzing collection {collection_name}: {e}")
                    database_schema[collection_name] = {}
            
            self.logger.info(f"Database schema analysis completed for {database_name}: {len(database_schema)} collections")
            return database_schema
            
        except Exception as e:
            self.logger.error(f"Error analyzing database schema for {database_name}: {e}")
            return {}
    
    def _convert_to_export_schema(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert documents to a simplified schema format suitable for export.
        
        Args:
            documents: List of MongoDB documents
            
        Returns:
            Simplified schema dictionary with field types
        """
        schema = {}
        
        for doc in documents:
            self._extract_schema_from_document(doc, schema)
        
        return schema
    
    def _extract_schema_from_document(self, doc: Dict[str, Any], schema: Dict[str, Any], prefix: str = "") -> None:
        """
        Recursively extract schema information from a document.
        
        Args:
            doc: Document to analyze
            schema: Schema dictionary to populate
            prefix: Field path prefix for nested objects
        """
        for key, value in doc.items():
            field_path = f"{prefix}.{key}" if prefix else key
            
            if value is None:
                schema[field_path] = "null"
            elif isinstance(value, ObjectId):
                schema[field_path] = "ObjectId"
            elif isinstance(value, bool):
                schema[field_path] = "boolean"
            elif isinstance(value, int):
                schema[field_path] = "int"
            elif isinstance(value, float):
                schema[field_path] = "float"
            elif isinstance(value, str):
                schema[field_path] = "string"
            elif isinstance(value, dict):
                # For nested objects, create a nested structure
                if field_path not in schema:
                    schema[field_path] = {}
                if isinstance(schema[field_path], dict):
                    self._extract_schema_from_document(value, schema[field_path])
                else:
                    # Convert to dict if it was a primitive type before
                    nested_schema = {}
                    self._extract_schema_from_document(value, nested_schema)
                    schema[field_path] = nested_schema
            elif isinstance(value, list):
                if not value:
                    schema[field_path] = "array"
                else:
                    # Analyze array elements
                    first_element = value[0]
                    if isinstance(first_element, dict):
                        # Array of objects
                        array_schema = {}
                        for item in value[:5]:  # Sample first 5 items
                            if isinstance(item, dict):
                                self._extract_schema_from_document(item, array_schema)
                        schema[field_path] = [array_schema] if array_schema else "array"
                    else:
                        # Array of primitives
                        element_type = self._get_primitive_type(first_element)
                        schema[field_path] = [element_type]
            else:
                # Handle other types (datetime, etc.)
                schema[field_path] = type(value).__name__
    
    def _get_primitive_type(self, value: Any) -> str:
        """Get the type name for primitive values."""
        if value is None:
            return "null"
        elif isinstance(value, ObjectId):
            return "ObjectId"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "string"
        else:
            return type(value).__name__

    def get_schema_summary(self, database_name: str, collection_name: str) -> str:
        """Get a human-readable summary of the collection schema."""
        schema = self.analyze_collection_schema(database_name, collection_name)
        
        if not schema['fields']:
            return "No fields found in collection"
        
        summary_lines = [f"Collection Schema ({schema['total_documents']} documents):"]
        
        for field in schema['fields'][:10]:  # Show top 10 fields
            presence_pct = field['presence_rate'] * 100
            summary_lines.append(
                f"• {field['name']} ({field['type']}) - {presence_pct:.1f}% present"
            )
        
        if len(schema['fields']) > 10:
            summary_lines.append(f"... and {len(schema['fields']) - 10} more fields")
        
        return "\n".join(summary_lines)
