#!/usr/bin/env python3
"""
Stemformatics MCP Server (Fixed Version)

This server provides access to Stemformatics data through the Model Context Protocol.
It handles requests for dataset metadata, sample information, and gene expression data.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any, Union
import pandas as pd
import numpy as np
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from utils import setup_cache, validate_config

# Load environment variables and configuration
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("stemformatics-mcp")

# Load configuration
CONFIG_PATH = os.getenv("CONFIG_PATH", "config.json")
try:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
    else:
        logger.warning(f"Config file not found at {CONFIG_PATH}, using example config")
        with open("config.example.json", 'r') as f:
            config = json.load(f)
            
    # Validate config
    validate_config(config)
    
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    sys.exit(1)

# Initialize API client and cache
cache = setup_cache(config)
BASE_URL = config["api_server"]["base_url"]
TIMEOUT = config["api_server"]["timeout"]
API_KEY = config["auth"]["api_key"] if config["auth"]["use_auth"] else None

# Initialize MCP server
mcp = FastMCP(
    config["server"]["name"], 
    description=config["server"]["description"]
)

def api_request(endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None) -> Dict:
    """Make a request to the Stemformatics API with proper error handling"""
    headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    
    try:
        # Check cache first if it's a GET request
        if method == "GET" and config["cache"]["enabled"]:
            cache_key = f"{url}_{str(params)}"
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
        
        # Make the request
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        # Handle different response types
        if response.headers.get('content-type') == 'application/json':
            result = response.json()
        else:
            # For raw file responses
            result = {'content': response.text, 'is_file': True}
        
        # Cache the result if it's a GET request
        if method == "GET" and config["cache"]["enabled"]:
            cache_key = f"{url}_{str(params)}"
            cache.set(cache_key, result)
            
        return result
    
    except requests.exceptions.RequestException as e:
        logger.error(f"API request error: {e}")
        return {"error": str(e)}

# Tool definitions

@mcp.tool()
def get_dataset_metadata(dataset_id: str) -> Dict:
    """
    Get metadata for a specific dataset.
    
    Args:
        dataset_id: The ID of the dataset
    
    Returns:
        Dictionary containing dataset metadata
    """
    return api_request(f"datasets/{dataset_id}/metadata")

@mcp.tool()
def get_dataset_samples(dataset_id: str, orient: str = "records", as_file: bool = False) -> Dict:
    """
    Get samples for a specific dataset.
    
    Args:
        dataset_id: The ID of the dataset
        orient: Orientation of the data (records, list, dict, etc.)
        as_file: Whether to return the data as a file
    
    Returns:
        Dictionary containing sample information
    """
    params = {"orient": orient, "as_file": str(as_file).lower()}
    return api_request(f"datasets/{dataset_id}/samples", params=params)

@mcp.tool()
def get_dataset_expression(dataset_id: str, gene_id: Optional[str] = None, key: str = "cpm", 
                           log2: bool = False, orient: str = "records", as_file: bool = False) -> Dict:
    """
    Get gene expression data for a dataset.
    
    Args:
        dataset_id: The ID of the dataset
        gene_id: Optional Ensembl gene ID to filter by
        key: Expression value key (default: cpm)
        log2: Whether to return log2 values
        orient: Orientation of the data (records, list, dict, etc.)
        as_file: Whether to return the data as a file
    
    Returns:
        Dictionary containing gene expression data
    """
    params = {
        "key": key,
        "log2": str(log2).lower(),
        "orient": orient,
        "as_file": str(as_file).lower()
    }
    
    if gene_id:
        params["gene_id"] = gene_id
        
    return api_request(f"datasets/{dataset_id}/expression", params=params)

# ... [other tool and resource definitions remain the same] ...

# The main execution section
if __name__ == "__main__":
    logger.info(f"Starting Stemformatics MCP Server with config from {CONFIG_PATH}")
    
    # Determine transport mode - default to stdio but support SSE as well
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    
    # Convert "network" to "sse" which is the valid transport name
    if transport == "network":
        transport = "sse"
        host = config["server"].get("host", "0.0.0.0")
        port = config["server"].get("port", 8080)
        logger.info(f"Starting server on {host}:{port} using SSE transport")
    
    logger.info(f"Using transport: {transport}")
    
    try:
        # We're simplifying the approach to avoid parameter issues
        # The mcp.run() implementation will handle the correct setup
        mcp.run(transport=transport)
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        sys.exit(1) 