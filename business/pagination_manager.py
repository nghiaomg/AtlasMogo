"""
Pagination Manager
Handles efficient pagination of MongoDB documents with caching and performance optimization.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import OrderedDict

logger = logging.getLogger(__name__)


@dataclass
class PageInfo:
    """Information about a specific page of documents."""
    page_number: int
    skip: int
    limit: int
    document_count: int
    total_documents: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginationManager:
    """Manages document pagination with caching and performance optimization."""
    
    def __init__(self, default_page_size: int = 50, max_cache_size: int = 10):
        """
        Initialize the pagination manager.
        
        Args:
            default_page_size: Default number of documents per page
            max_cache_size: Maximum number of pages to cache in memory
        """
        self.default_page_size = default_page_size
        self.max_cache_size = max_cache_size
        
        # Cache for loaded pages (page_number -> documents)
        self._page_cache: OrderedDict[int, List[Dict[str, Any]]] = OrderedDict()
        
        # Current page information
        self._current_page = 1
        self._total_documents = 0
        self._current_query = ""
        self._current_sort = None
        
        # Performance tracking
        self._cache_hits = 0
        self._cache_misses = 0
    
    def get_page_info(self, page_number: int, total_documents: int, page_size: int = None) -> PageInfo:
        """
        Get information about a specific page.
        
        Args:
            page_number: Page number (1-based)
            total_documents: Total number of documents in collection
            page_size: Number of documents per page
            
        Returns:
            PageInfo object with pagination details
        """
        if page_size is None:
            page_size = self.default_page_size
        
        if page_size <= 0:
            page_size = self.default_page_size
        
        if page_number < 1:
            page_number = 1
        
        total_pages = max(1, (total_documents + page_size - 1) // page_size)
        page_number = min(page_number, total_pages)
        
        skip = (page_number - 1) * page_size
        document_count = min(page_size, total_documents - skip)
        
        return PageInfo(
            page_number=page_number,
            skip=skip,
            limit=page_size,
            document_count=document_count,
            total_documents=total_documents,
            total_pages=total_pages,
            has_next=page_number < total_pages,
            has_previous=page_number > 1
        )
    
    def get_page_range(self, current_page: int, total_pages: int, max_visible: int = 5) -> List[int]:
        """
        Get a range of page numbers to display in pagination controls.
        
        Args:
            current_page: Current page number
            total_pages: Total number of pages
            max_visible: Maximum number of page numbers to show
            
        Returns:
            List of page numbers to display
        """
        if total_pages <= max_visible:
            return list(range(1, total_pages + 1))
        
        # Calculate start and end of visible range
        half_visible = max_visible // 2
        start = max(1, current_page - half_visible)
        end = min(total_pages, start + max_visible - 1)
        
        # Adjust start if we're near the end
        if end - start + 1 < max_visible:
            start = max(1, end - max_visible + 1)
        
        return list(range(start, end + 1))
    
    def is_page_cached(self, page_number: int) -> bool:
        """Check if a specific page is cached."""
        return page_number in self._page_cache
    
    def get_cached_page(self, page_number: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get a cached page if available.
        
        Args:
            page_number: Page number to retrieve
            
        Returns:
            Cached documents or None if not cached
        """
        if page_number in self._page_cache:
            # Move to end (most recently used)
            documents = self._page_cache.pop(page_number)
            self._page_cache[page_number] = documents
            self._cache_hits += 1
            logger.debug(f"Cache hit for page {page_number}")
            return documents
        
        self._cache_misses += 1
        logger.debug(f"Cache miss for page {page_number}")
        return None
    
    def cache_page(self, page_number: int, documents: List[Dict[str, Any]]) -> None:
        """
        Cache a page of documents.
        
        Args:
            page_number: Page number to cache
            documents: Documents to cache
        """
        # Remove oldest page if cache is full
        if len(self._page_cache) >= self.max_cache_size:
            oldest_page = next(iter(self._page_cache))
            self._page_cache.pop(oldest_page)
            logger.debug(f"Removed page {oldest_page} from cache (cache full)")
        
        self._page_cache[page_number] = documents
        logger.debug(f"Cached page {page_number} with {len(documents)} documents")
    
    def clear_cache(self) -> None:
        """Clear all cached pages."""
        cache_size = len(self._page_cache)
        self._page_cache.clear()
        logger.info(f"Cleared pagination cache ({cache_size} pages)")
    
    def clear_cache_for_query(self, query: str, sort: List[Tuple[str, int]] = None) -> None:
        """
        Clear cache when query or sort changes.
        
        Args:
            query: New query string
            sort: New sort criteria
        """
        if query != self._current_query or sort != self._current_sort:
            cache_size = len(self._page_cache)
            self._page_cache.clear()
            self._current_query = query
            self._current_sort = sort
            logger.info(f"Query/sort changed, cleared pagination cache ({cache_size} pages)")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        return {
            "cache_size": len(self._page_cache),
            "max_cache_size": self.max_cache_size,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": self._cache_hits / (self._cache_hits + self._cache_misses) if (self._cache_hits + self._cache_misses) > 0 else 0,
            "cached_pages": list(self._page_cache.keys())
        }
    
    def optimize_cache(self, frequently_accessed_pages: List[int]) -> None:
        """
        Optimize cache by prioritizing frequently accessed pages.
        
        Args:
            frequently_accessed_pages: List of page numbers that are accessed often
        """
        # Keep frequently accessed pages in cache
        optimized_cache = OrderedDict()
        
        for page_num in frequently_accessed_pages:
            if page_num in self._page_cache:
                optimized_cache[page_num] = self._page_cache[page_num]
        
        # Add remaining cached pages up to max size
        for page_num, documents in self._page_cache.items():
            if page_num not in optimized_cache and len(optimized_cache) < self.max_cache_size:
                optimized_cache[page_num] = documents
        
        self._page_cache = optimized_cache
        logger.info(f"Cache optimized: {len(self._page_cache)} pages retained")
    
    def get_memory_usage_estimate(self) -> Dict[str, Any]:
        """Estimate memory usage of cached pages."""
        total_docs = sum(len(docs) for docs in self._page_cache.values())
        avg_doc_size = 1024  # Rough estimate: 1KB per document
        
        return {
            "cached_pages": len(self._page_cache),
            "total_cached_documents": total_docs,
            "estimated_memory_mb": (total_docs * avg_doc_size) / (1024 * 1024),
            "cache_efficiency": len(self._page_cache) / self.max_cache_size if self.max_cache_size > 0 else 0
        }
