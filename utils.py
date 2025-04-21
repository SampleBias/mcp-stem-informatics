"""
Utility functions for the Stemformatics MCP Server.
"""

import os
import sys
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger("stemformatics-mcp")

class SimpleCache:
    """A simple in-memory cache with TTL support"""
    
    def __init__(self, ttl_seconds: int = 3600, max_size_mb: int = 100):
        self.cache = {}
        self.ttl_seconds = ttl_seconds
        self.max_size_mb = max_size_mb
        self.current_size_bytes = 0
        
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache if it exists and hasn't expired"""
        if key not in self.cache:
            return None
            
        entry = self.cache[key]
        if datetime.now() > entry["expires"]:
            # Remove expired entry
            self._remove_entry(key)
            return None
            
        return entry["value"]
        
    def set(self, key: str, value: Any) -> bool:
        """Set a value in the cache with the configured TTL"""
        # Roughly estimate the size of the value
        try:
            value_size = len(json.dumps(value).encode("utf-8"))
        except:
            value_size = sys.getsizeof(value)
            
        # Check if adding this would exceed max cache size
        if key in self.cache:
            old_size = len(json.dumps(self.cache[key]["value"]).encode("utf-8"))
            size_diff = value_size - old_size
            new_total = self.current_size_bytes + size_diff
        else:
            new_total = self.current_size_bytes + value_size
            
        max_bytes = self.max_size_mb * 1024 * 1024
        if new_total > max_bytes:
            # Need to evict some entries
            self._evict(new_total - max_bytes)
            
        # Add the new entry
        self.cache[key] = {
            "value": value,
            "expires": datetime.now() + timedelta(seconds=self.ttl_seconds),
            "size": value_size
        }
        
        # Update current size
        if key in self.cache:
            old_size = self.cache[key].get("size", 0)
            self.current_size_bytes = self.current_size_bytes - old_size + value_size
        else:
            self.current_size_bytes += value_size
            
        return True
        
    def _remove_entry(self, key: str) -> None:
        """Remove an entry from the cache"""
        if key in self.cache:
            self.current_size_bytes -= self.cache[key].get("size", 0)
            del self.cache[key]
            
    def _evict(self, bytes_to_free: int) -> None:
        """Evict entries to free up space"""
        # Sort by expiration time, oldest first
        sorted_entries = sorted(
            [(k, v["expires"]) for k, v in self.cache.items()],
            key=lambda x: x[1]
        )
        
        bytes_freed = 0
        for key, _ in sorted_entries:
            if bytes_freed >= bytes_to_free:
                break
                
            entry_size = self.cache[key].get("size", 0)
            self._remove_entry(key)
            bytes_freed += entry_size
            
def validate_config(config: Dict) -> bool:
    """
    Validate the configuration dictionary.
    Raises ValueError if invalid.
    """
    required_sections = ["api_server", "auth", "cache", "server"]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required config section: {section}")
            
    # Check api_server section
    if "base_url" not in config["api_server"]:
        raise ValueError("Missing base_url in api_server config")
    if "timeout" not in config["api_server"]:
        config["api_server"]["timeout"] = 30
        
    # Check auth section
    if "use_auth" not in config["auth"]:
        config["auth"]["use_auth"] = False
    if config["auth"]["use_auth"] and "api_key" not in config["auth"]:
        raise ValueError("API key required when use_auth is true")
        
    # Check cache section
    if "enabled" not in config["cache"]:
        config["cache"]["enabled"] = True
    if "ttl_seconds" not in config["cache"]:
        config["cache"]["ttl_seconds"] = 3600
    if "max_size_mb" not in config["cache"]:
        config["cache"]["max_size_mb"] = 100
        
    # Check server section
    if "name" not in config["server"]:
        config["server"]["name"] = "Stemformatics MCP Server"
    if "description" not in config["server"]:
        config["server"]["description"] = "MCP server for accessing stem cell data"
        
    return True
    
def setup_cache(config: Dict) -> SimpleCache:
    """Set up and return a cache instance based on configuration"""
    if not config["cache"]["enabled"]:
        # Return dummy cache that doesn't actually cache
        class DummyCache:
            def get(self, key): return None
            def set(self, key, value): return True
            
        return DummyCache()
        
    return SimpleCache(
        ttl_seconds=config["cache"]["ttl_seconds"],
        max_size_mb=config["cache"]["max_size_mb"]
    ) 