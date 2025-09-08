"""
Database Exporter
Handles exporting a full MongoDB database to various formats (JSON, BSON, ZIP).
"""

import json
import logging
import os
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import bson
from bson import json_util

logger = logging.getLogger(__name__)


class DatabaseExporter:
    """Exports a full MongoDB database to various file formats."""

    def __init__(self, mongo_service, database_name: str):
        self.mongo_service = mongo_service
        self.database_name = database_name

    def export_database(
        self, 
        output_path: str, 
        export_format: str = "json", 
        use_compression: bool = False
    ) -> tuple[bool, str]:
        """
        Orchestrates the database export process.

        Args:
            output_path: The directory or file path for the export.
            export_format: The format to export to ('json' or 'bson').
            use_compression: Whether to compress the output into a ZIP file.

        Returns:
            A tuple (success, message).
        """
        try:
            collections = self.mongo_service.get_collections(self.database_name)
            if not collections:
                return False, f"No collections found in database '{self.database_name}'."

            export_dir = self._create_export_directory(output_path, use_compression)
            if not export_dir:
                return False, "Failed to create export directory."

            for collection_name in collections:
                logger.info(f"Exporting collection: {collection_name}")
                documents = self.mongo_service.find_documents(
                    self.database_name, collection_name, limit=0  # No limit
                )

                if export_format == "json":
                    self._export_collection_to_json(documents, collection_name, export_dir)
                elif export_format == "bson":
                    self._export_collection_to_bson(documents, collection_name, export_dir)
            
            if use_compression:
                final_path = self._compress_directory(export_dir, output_path)
                return True, f"Database exported successfully to {final_path}"
            else:
                return True, f"Database exported successfully to {export_dir}"

        except Exception as e:
            logger.error(f"Database export failed: {e}", exc_info=True)
            return False, f"An error occurred during export: {e}"

    def _create_export_directory(self, output_path: str, use_compression: bool) -> Optional[str]:
        """
        Creates the target directory for the export files.
        """
        try:
            if use_compression:
                # For ZIP, create a temporary directory
                temp_dir = Path(output_path).parent / f"atlasmogo_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                temp_dir.mkdir(parents=True, exist_ok=True)
                return str(temp_dir)
            else:
                # For folder export, use the specified path
                Path(output_path).mkdir(parents=True, exist_ok=True)
                return output_path
        except Exception as e:
            logger.error(f"Failed to create directory at {output_path}: {e}")
            return None

    def _export_collection_to_json(self, documents: List[Dict[str, Any]], collection_name: str, export_dir: str):
        """
        Exports a single collection to a JSON file.
        """
        file_path = Path(export_dir) / f"{collection_name}.json"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Use json_util to handle MongoDB specific types like ObjectId
                f.write(json_util.dumps(documents, indent=2))
            logger.info(f"Successfully exported {collection_name} to {file_path}")
        except Exception as e:
            logger.error(f"Failed to export {collection_name} to JSON: {e}")

    def _export_collection_to_bson(self, documents: List[Dict[str, Any]], collection_name: str, export_dir: str):
        """
        Exports a single collection to a BSON file.
        """
        file_path = Path(export_dir) / f"{collection_name}.bson"
        try:
            with open(file_path, 'wb') as f:
                for doc in documents:
                    f.write(bson.encode(doc))
            logger.info(f"Successfully exported {collection_name} to {file_path}")
        except Exception as e:
            logger.error(f"Failed to export {collection_name} to BSON: {e}")

    def _compress_directory(self, source_dir: str, output_zip_path: str) -> str:
        """
        Compresses the contents of a directory into a ZIP file.
        """
        source_path = Path(source_dir)
        zip_path = Path(output_zip_path)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_path.rglob('*'):
                arcname = file_path.relative_to(source_path)
                zipf.write(file_path, arcname)
        
        # Clean up the temporary directory
        import shutil
        try:
            shutil.rmtree(source_dir)
            logger.info(f"Removed temporary directory: {source_dir}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary directory {source_dir}: {e}")

        return str(zip_path)

