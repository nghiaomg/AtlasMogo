"""
Database Importer
Handles importing a full MongoDB database from JSON, BSON, or ZIP (containing per-collection files).
"""

import json
import logging
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import bson
from bson import json_util

logger = logging.getLogger(__name__)


class DatabaseImporter:
    """Imports collections and documents into a MongoDB database."""

    def __init__(self, mongo_service, database_name: str):
        self.mongo_service = mongo_service
        self.database_name = database_name

    def import_database(
        self,
        source_path: str,
        overwrite_policy: Dict[str, bool] | None = None,
    ) -> Tuple[bool, str]:
        """
        Import a database from a JSON/BSON/ZIP file or a directory containing per-collection files.

        Args:
            source_path: Path to .json/.bson/.zip file or a directory
            overwrite_policy: Optional map {collection_name: overwrite?}

        Returns:
            (success, message)
        """
        try:
            p = Path(source_path)
            if not p.exists():
                return False, f"Source not found: {source_path}"

            # Resolve into a temp directory containing per-collection files
            if p.is_dir():
                work_dir = str(p)
            elif p.suffix.lower() == ".zip":
                work_dir = self._unzip_to_temp(source_path)
            elif p.suffix.lower() in (".json", ".bson"):
                # Single file; place into a temp dir to normalize flow
                tmp_dir = tempfile.mkdtemp(prefix="atlasmogo_import_")
                shutil.copy2(str(p), os.path.join(tmp_dir, p.name))
                work_dir = tmp_dir
            else:
                return False, f"Unsupported source type: {p.suffix}"

            # Discover collections to import from the directory
            collection_files = self._discover_collection_files(work_dir)
            if not collection_files:
                # Try combined JSON format (single file mapping collection -> docs)
                combined = self._find_combined_json(work_dir)
                if not combined:
                    return False, "No importable files found (expected *.json/*.bson)."
                return self._import_from_combined_json(combined, overwrite_policy)

            # Import per-collection files
            for collection_name, file_path in collection_files:
                if overwrite_policy and collection_name in overwrite_policy and overwrite_policy[collection_name]:
                    # Drop collection before import
                    try:
                        self.mongo_service.drop_collection(self.database_name, collection_name)
                    except Exception as e:
                        logger.warning(f"Failed to drop existing collection {collection_name}: {e}")

                suffix = Path(file_path).suffix.lower()
                if suffix == ".json":
                    documents = self._load_json_documents(file_path)
                elif suffix == ".bson":
                    documents = self._load_bson_documents(file_path)
                else:
                    logger.info(f"Skipping unsupported file: {file_path}")
                    continue

                self._bulk_insert(collection_name, documents)

            return True, f"Imported {len(collection_files)} collections into '{self.database_name}'"
        except Exception as e:
            logger.error(f"Database import failed: {e}", exc_info=True)
            return False, f"An error occurred during import: {e}"
        finally:
            # Cleanup temp dirs created by unzip/copy
            self._cleanup_temp_dirs()

    # ---- helpers ----

    _temp_dirs: List[str] = []

    def _unzip_to_temp(self, zip_path: str) -> str:
        tmp_dir = tempfile.mkdtemp(prefix="atlasmogo_unzip_")
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(tmp_dir)
        self._temp_dirs.append(tmp_dir)
        return tmp_dir

    def _cleanup_temp_dirs(self) -> None:
        for d in self._temp_dirs:
            try:
                shutil.rmtree(d)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp dir {d}: {e}")
        self._temp_dirs.clear()

    def _discover_collection_files(self, directory: str) -> List[Tuple[str, str]]:
        files: List[Tuple[str, str]] = []
        for path in Path(directory).rglob('*'):
            if not path.is_file():
                continue
            if path.suffix.lower() not in (".json", ".bson"):
                continue
            # collection name is filename without extension
            collection_name = path.stem
            files.append((collection_name, str(path)))
        return files

    def _find_combined_json(self, directory: str) -> Optional[str]:
        # Heuristic: first *.json whose top-level is a dict mapping to list
        for path in Path(directory).glob('*.json'):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    return str(path)
            except Exception:
                continue
        return None

    def _import_from_combined_json(self, json_file: str, overwrite_policy: Dict[str, bool] | None) -> Tuple[bool, str]:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return False, "Combined JSON format invalid (expected object of collections)."

        imported = 0
        for collection_name, docs in data.items():
            if overwrite_policy and overwrite_policy.get(collection_name):
                try:
                    self.mongo_service.drop_collection(self.database_name, collection_name)
                except Exception as e:
                    logger.warning(f"Failed to drop existing collection {collection_name}: {e}")

            if not isinstance(docs, list):
                logger.warning(f"Collection '{collection_name}' is not a list, skipping.")
                continue
            self._bulk_insert(collection_name, docs)
            imported += 1
        return True, f"Imported {imported} collections into '{self.database_name}' from combined JSON"

    def _load_json_documents(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Support Extended JSON
            try:
                return json.loads(f.read(), object_hook=json_util.object_hook)
            except Exception:
                f.seek(0)
                return json.load(f)

    def _load_bson_documents(self, file_path: str) -> List[Dict[str, Any]]:
        docs: List[Dict[str, Any]] = []
        with open(file_path, 'rb') as f:
            # Files contain concatenated BSON documents
            while True:
                try:
                    doc = bson.decode_file_iter(f).__next__()
                    docs.append(doc)
                except StopIteration:
                    break
                except Exception:
                    break
        return docs

    def _bulk_insert(self, collection_name: str, documents: List[Dict[str, Any]]) -> None:
        if not documents:
            return
        # Insert in batches to avoid huge payloads
        batch_size = 1000
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            try:
                from data.mongo_repository import MongoRepository
                client = self.mongo_service._connection.get_client()
                if not client:
                    raise RuntimeError("No MongoDB client available")
                repo = MongoRepository(client)
                repo.insert_many(self.database_name, collection_name, batch)
            except Exception as e:
                logger.error(f"Batch insert failed for {collection_name}: {e}")
                raise
