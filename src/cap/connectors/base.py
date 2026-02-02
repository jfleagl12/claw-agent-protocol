"""
Base Connector Interface

All CAP connectors must implement this interface to provide standardized
access to external data sources.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import hashlib
import json


class CAPConnector(ABC):
    """Base class for all CAP connectors."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the connector.
        
        Args:
            config: Connector-specific configuration
        """
        self.config = config
        self.name = self.__class__.__name__
        self._authenticated = False
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Authenticate with the external service.
        
        Returns:
            True if authentication successful
        """
        pass
    
    @abstractmethod
    def get_supported_shelves(self) -> List[str]:
        """
        Get list of shelves this connector supports.
        
        Returns:
            List of shelf names (e.g., ["identity", "calendar"])
        """
        pass
    
    # ========================================================================
    # Shelf-specific fetch methods (implement as needed)
    # ========================================================================
    
    async def fetch_identity(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Fetch identity data (contacts, people, orgs).
        
        Args:
            filters: Optional filters
        
        Returns:
            List of normalized identity objects
        """
        raise NotImplementedError(f"{self.name} does not support identity shelf")
    
    async def fetch_calendar(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch calendar data (events, availability).
        
        Args:
            start_date: ISO8601 date string
            end_date: ISO8601 date string
        
        Returns:
            List of normalized calendar objects
        """
        raise NotImplementedError(f"{self.name} does not support calendar shelf")
    
    async def fetch_comms(
        self,
        since: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Fetch communications data (emails, messages).
        
        Args:
            since: ISO8601 timestamp
            limit: Maximum number of items
        
        Returns:
            List of normalized comms objects
        """
        raise NotImplementedError(f"{self.name} does not support comms shelf")
    
    async def fetch_docs(
        self,
        query: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Fetch documents data (notes, files, snippets).
        
        Args:
            query: Search query
            limit: Maximum number of items
        
        Returns:
            List of normalized docs objects
        """
        raise NotImplementedError(f"{self.name} does not support docs shelf")
    
    async def fetch_tasks(
        self,
        status: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Fetch tasks data (tasks, projects, milestones).
        
        Args:
            status: Filter by status
            limit: Maximum number of items
        
        Returns:
            List of normalized tasks objects
        """
        raise NotImplementedError(f"{self.name} does not support tasks shelf")
    
    # ========================================================================
    # Utility methods
    # ========================================================================
    
    def create_source_pointer(self, raw_data: Dict, external_id: str, url: Optional[str] = None) -> Dict:
        """
        Create a source pointer for provenance tracking.
        
        Args:
            raw_data: The raw data from the source
            external_id: The external system's ID for this object
            url: Optional URL to the source object
        
        Returns:
            Source pointer dict
        """
        return {
            "system": self.name.lower().replace("connector", ""),
            "external_id": external_id,
            "url": url,
            "hash": hashlib.sha256(
                json.dumps(raw_data, sort_keys=True).encode()
            ).hexdigest()
        }
    
    def get_default_date_range(self) -> tuple[str, str]:
        """
        Get default date range for queries.
        
        Returns:
            Tuple of (start_date, end_date) as ISO8601 strings
        """
        now = datetime.now()
        start = now.date().isoformat()
        end = (now + timedelta(days=30)).date().isoformat()
        return start, end
    
    def get_default_since(self, days: int = 7) -> str:
        """
        Get default 'since' timestamp.
        
        Args:
            days: Number of days back
        
        Returns:
            ISO8601 timestamp
        """
        return (datetime.now() - timedelta(days=days)).isoformat()
