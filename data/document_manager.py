"""
Document Manager
Provides bulk document operations such as bulk delete using _id list.
"""

from __future__ import annotations

from typing import List
import logging

from bson import ObjectId

logger = logging.getLogger(__name__)


def delete_documents(collection, ids: List[ObjectId]) -> int:
    """Delete multiple documents by their ObjectId using a single delete_many call.

    Args:
        collection: A pymongo Collection instance
        ids: List of ObjectId to delete

    Returns:
        The number of documents deleted
    """
    if not ids:
        return 0
    try:
        result = collection.delete_many({"_id": {"$in": ids}})
        return result.deleted_count
    except Exception as e:
        logger.error(f"Bulk delete failed: {e}")
        raise
