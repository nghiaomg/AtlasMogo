"""
Schema Exporter
Handles exporting MongoDB database schemas to various formats (JSON, YAML, Markdown).
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)


class SchemaExporter:
    """Exports MongoDB database schemas to various file formats."""
    
    def __init__(self):
        """Initialize the schema exporter."""
        self.logger = logging.getLogger(__name__)
    
    def export_to_json(self, schema_data: Dict[str, Dict[str, Any]], 
                      file_path: str, database_name: str) -> bool:
        """
        Export schema data to JSON format.
        
        Args:
            schema_data: Dictionary containing schema information for all collections
            file_path: Path where the JSON file should be saved
            database_name: Name of the database being exported
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            export_data = {
                "database": database_name,
                "exported_at": datetime.now().isoformat(),
                "collections": schema_data,
                "metadata": {
                    "total_collections": len(schema_data),
                    "export_format": "json",
                    "generated_by": "AtlasMogo Schema Exporter"
                }
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Schema exported to JSON: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {e}")
            return False
    
    def export_to_yaml(self, schema_data: Dict[str, Dict[str, Any]], 
                      file_path: str, database_name: str) -> bool:
        """
        Export schema data to YAML format.
        
        Args:
            schema_data: Dictionary containing schema information for all collections
            file_path: Path where the YAML file should be saved
            database_name: Name of the database being exported
            
        Returns:
            True if export was successful, False otherwise
        """
        if yaml is None:
            self.logger.error("PyYAML is not installed. Cannot export to YAML format.")
            return False
        
        try:
            export_data = {
                "database": database_name,
                "exported_at": datetime.now().isoformat(),
                "collections": schema_data,
                "metadata": {
                    "total_collections": len(schema_data),
                    "export_format": "yaml",
                    "generated_by": "AtlasMogo Schema Exporter"
                }
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(export_data, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
            
            self.logger.info(f"Schema exported to YAML: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to YAML: {e}")
            return False
    
    def export_to_markdown(self, schema_data: Dict[str, Dict[str, Any]], 
                          file_path: str, database_name: str) -> bool:
        """
        Export schema data to Markdown format with nicely formatted documentation.
        
        Args:
            schema_data: Dictionary containing schema information for all collections
            file_path: Path where the Markdown file should be saved
            database_name: Name of the database being exported
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            md_content = self._generate_markdown_content(schema_data, database_name)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            self.logger.info(f"Schema exported to Markdown: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to Markdown: {e}")
            return False
    
    def _generate_markdown_content(self, schema_data: Dict[str, Dict[str, Any]], 
                                  database_name: str) -> str:
        """
        Generate Markdown content from schema data.
        
        Args:
            schema_data: Dictionary containing schema information for all collections
            database_name: Name of the database being exported
            
        Returns:
            Formatted Markdown string
        """
        lines = [
            f"# Database Schema: {database_name}",
            "",
            f"**Generated by:** AtlasMogo Schema Exporter",
            f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Collections:** {len(schema_data)}",
            "",
            "## Collections Overview",
            ""
        ]
        
        # Add table of contents
        for collection_name in sorted(schema_data.keys()):
            lines.append(f"- [{collection_name}](#{collection_name.lower().replace('_', '-')})")
        
        lines.append("")
        
        # Add detailed schema for each collection
        for collection_name in sorted(schema_data.keys()):
            collection_schema = schema_data[collection_name]
            lines.extend(self._format_collection_markdown(collection_name, collection_schema))
        
        return "\n".join(lines)
    
    def _format_collection_markdown(self, collection_name: str, 
                                   schema: Dict[str, Any]) -> list:
        """
        Format a single collection's schema as Markdown.
        
        Args:
            collection_name: Name of the collection
            schema: Schema dictionary for the collection
            
        Returns:
            List of Markdown lines for this collection
        """
        lines = [
            f"## {collection_name}",
            ""
        ]
        
        if not schema:
            lines.extend([
                "*No documents found in this collection.*",
                ""
            ])
            return lines
        
        # Add schema as formatted JSON
        lines.extend([
            "### Schema Structure",
            "",
            "```json",
            json.dumps(schema, indent=2, ensure_ascii=False, default=str),
            "```",
            ""
        ])
        
        # Add field summary table
        field_list = self._extract_field_list(schema)
        if field_list:
            lines.extend([
                "### Fields Summary",
                "",
                "| Field | Type | Description |",
                "|-------|------|-------------|"
            ])
            
            for field_path, field_type in sorted(field_list):
                description = self._get_field_description(field_path, field_type)
                lines.append(f"| `{field_path}` | `{field_type}` | {description} |")
            
            lines.append("")
        
        return lines
    
    def _extract_field_list(self, schema: Dict[str, Any], prefix: str = "") -> list:
        """
        Extract a flat list of fields from nested schema.
        
        Args:
            schema: Schema dictionary
            prefix: Field path prefix
            
        Returns:
            List of (field_path, field_type) tuples
        """
        fields = []
        
        for key, value in schema.items():
            field_path = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                # Nested object
                fields.append((field_path, "object"))
                fields.extend(self._extract_field_list(value, field_path))
            elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                # Array of objects
                fields.append((field_path, "array[object]"))
                fields.extend(self._extract_field_list(value[0], f"{field_path}[]"))
            elif isinstance(value, list) and len(value) > 0:
                # Array of primitives
                element_type = value[0]
                fields.append((field_path, f"array[{element_type}]"))
            else:
                # Primitive type
                fields.append((field_path, str(value)))
        
        return fields
    
    def _get_field_description(self, field_path: str, field_type: str) -> str:
        """
        Generate a description for a field based on its path and type.
        
        Args:
            field_path: Path to the field
            field_type: Type of the field
            
        Returns:
            Description string
        """
        descriptions = {
            "_id": "MongoDB document identifier",
            "ObjectId": "MongoDB ObjectId reference",
            "string": "Text value",
            "int": "Integer number",
            "float": "Decimal number",
            "boolean": "True/false value",
            "array": "List of values",
            "object": "Nested document",
            "null": "Null value",
            "datetime": "Date and time value"
        }
        
        # Check for common field names
        field_name = field_path.split('.')[-1].lower()
        if field_name in ['id', '_id']:
            return descriptions.get("_id", "Document identifier")
        elif 'email' in field_name:
            return "Email address"
        elif 'name' in field_name:
            return "Name field"
        elif 'date' in field_name or 'time' in field_name:
            return "Date/time field"
        elif 'url' in field_name or 'link' in field_name:
            return "URL/link field"
        elif 'count' in field_name or 'total' in field_name:
            return "Count/total field"
        
        # Default to type-based description
        return descriptions.get(field_type, f"{field_type} field")
    
    def get_supported_formats(self) -> Dict[str, Dict[str, str]]:
        """
        Get information about supported export formats.
        
        Returns:
            Dictionary with format information
        """
        formats = {
            "json": {
                "name": "JSON",
                "extension": ".json",
                "description": "JavaScript Object Notation format",
                "available": True
            },
            "yaml": {
                "name": "YAML",
                "extension": ".yaml",
                "description": "YAML Ain't Markup Language format",
                "available": yaml is not None
            },
            "markdown": {
                "name": "Markdown",
                "extension": ".md",
                "description": "Markdown documentation format",
                "available": True
            }
        }
        
        return formats
    
    def export_schema(self, schema_data: Dict[str, Dict[str, Any]], 
                     file_path: str, database_name: str, 
                     format_type: str = "json") -> bool:
        """
        Export schema data to the specified format.
        
        Args:
            schema_data: Dictionary containing schema information for all collections
            file_path: Path where the file should be saved
            database_name: Name of the database being exported
            format_type: Export format ("json", "yaml", or "markdown")
            
        Returns:
            True if export was successful, False otherwise
        """
        format_type = format_type.lower()
        
        if format_type == "json":
            return self.export_to_json(schema_data, file_path, database_name)
        elif format_type == "yaml":
            return self.export_to_yaml(schema_data, file_path, database_name)
        elif format_type == "markdown":
            return self.export_to_markdown(schema_data, file_path, database_name)
        else:
            self.logger.error(f"Unsupported export format: {format_type}")
            return False
