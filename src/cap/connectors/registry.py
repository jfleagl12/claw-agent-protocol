"""
Connector Registry

Manages the lifecycle and discovery of CAP connectors.
"""

from typing import Dict, List
import logging
from cap.connectors.base import CAPConnector

logger = logging.getLogger(__name__)


class ConnectorRegistry:
    """Registry for managing CAP connectors."""
    
    def __init__(self, config):
        """
        Initialize the connector registry.
        
        Args:
            config: Server configuration
        """
        self.config = config
        self._connectors: List[CAPConnector] = []
        self._shelf_map: Dict[str, List[CAPConnector]] = {}
    
    def initialize(self):
        """Initialize all enabled connectors."""
        enabled = self.config.enabled_connectors
        
        for connector_name in enabled:
            try:
                connector = self._load_connector(connector_name)
                self._connectors.append(connector)
                
                # Map connector to shelves
                for shelf in connector.get_supported_shelves():
                    if shelf not in self._shelf_map:
                        self._shelf_map[shelf] = []
                    self._shelf_map[shelf].append(connector)
                
                logger.info(f"Loaded connector: {connector_name}")
            except Exception as e:
                logger.error(f"Failed to load connector {connector_name}: {e}")
    
    def _load_connector(self, name: str) -> CAPConnector:
        """
        Dynamically load a connector by name.
        
        Args:
            name: Connector name (e.g., "google_calendar")
        
        Returns:
            Initialized connector instance
        """
        # Import the connector module
        if name == "google_calendar":
            from cap.connectors.google_calendar import GoogleCalendarConnector
            connector_class = GoogleCalendarConnector
        elif name == "gmail":
            from cap.connectors.gmail import GmailConnector
            connector_class = GmailConnector
        else:
            raise ValueError(f"Unknown connector: {name}")
        
        # Get connector-specific config
        connector_config = self.config.connector_configs.get(name, {})
        
        # Initialize
        return connector_class(connector_config)
    
    def get_connectors_for_shelf(self, shelf: str) -> List[CAPConnector]:
        """
        Get all connectors that support a given shelf.
        
        Args:
            shelf: Shelf name (e.g., "calendar")
        
        Returns:
            List of connectors
        """
        return self._shelf_map.get(shelf, [])
    
    def get_all_connectors(self) -> List[CAPConnector]:
        """Get all registered connectors."""
        return self._connectors
