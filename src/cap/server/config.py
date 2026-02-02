"""
Server Configuration

Handles configuration loading from environment variables and config files.
"""

import os
from typing import Any, Dict, List
from dataclasses import dataclass, field


@dataclass
class ServerConfig:
    """CAP server configuration."""
    
    # Server settings
    server_name: str = "claw-agent-protocol"
    server_version: str = "2.0.0"
    
    # Cache settings
    cache_ttl: int = 300  # 5 minutes default
    cache_backend: str = "memory"  # "memory" or "redis"
    redis_url: str = ""
    
    # Connector settings
    enabled_connectors: List[str] = field(default_factory=list)
    connector_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls) -> "ServerConfig":
        """
        Load configuration from environment variables.
        
        Environment variables:
            CAP_CONNECTORS: Comma-separated list of enabled connectors
            CAP_CACHE_TTL: Cache TTL in seconds
            CAP_CACHE_BACKEND: "memory" or "redis"
            CAP_REDIS_URL: Redis connection URL (if using Redis)
            CAP_<CONNECTOR>_*: Connector-specific config
        
        Returns:
            ServerConfig instance
        """
        config = cls()
        
        # Load enabled connectors
        connectors_str = os.getenv("CAP_CONNECTORS", "")
        if connectors_str:
            config.enabled_connectors = [c.strip() for c in connectors_str.split(",")]
        
        # Load cache settings
        config.cache_ttl = int(os.getenv("CAP_CACHE_TTL", "300"))
        config.cache_backend = os.getenv("CAP_CACHE_BACKEND", "memory")
        config.redis_url = os.getenv("CAP_REDIS_URL", "")
        
        # Load connector-specific configs
        config.connector_configs = cls._load_connector_configs()
        
        return config
    
    @classmethod
    def _load_connector_configs(cls) -> Dict[str, Dict[str, Any]]:
        """
        Load connector-specific configuration from environment.
        
        Example:
            CAP_GOOGLE_CALENDAR_ACCESS_TOKEN=abc123
            CAP_GMAIL_ACCESS_TOKEN=xyz789
        
        Returns:
            Dict mapping connector names to their configs
        """
        configs = {}
        
        # Scan environment for connector configs
        for key, value in os.environ.items():
            if key.startswith("CAP_") and "_" in key[4:]:
                parts = key[4:].split("_", 1)
                if len(parts) == 2:
                    connector_name = parts[0].lower()
                    config_key = parts[1].lower()
                    
                    if connector_name not in configs:
                        configs[connector_name] = {}
                    
                    configs[connector_name][config_key] = value
        
        return configs
