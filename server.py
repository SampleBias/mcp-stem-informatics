#!/usr/bin/env python3
"""
Stemformatics MCP Server

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
        result = response.json()
        
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
def list_datasets(limit: int = 10, offset: int = 0, filter_criteria: Optional[str] = None) -> Dict:
    """
    Get a list of available datasets.
    
    Args:
        limit: Maximum number of datasets to return
        offset: Offset for pagination
        filter_criteria: Optional JSON string with filter criteria
    
    Returns:
        Dictionary containing dataset information
    """
    params = {"limit": limit, "offset": offset}
    if filter_criteria:
        try:
            filter_dict = json.loads(filter_criteria)
            params.update(filter_dict)
        except json.JSONDecodeError:
            return {"error": "Invalid filter_criteria JSON string"}
    
    return api_request("datasets", params=params)

@mcp.tool()
def get_dataset_metadata(dataset_id: str) -> Dict:
    """
    Get metadata for a specific dataset.
    
    Args:
        dataset_id: The ID of the dataset
    
    Returns:
        Dictionary containing dataset metadata
    """
    return api_request(f"datasets/{dataset_id}")

@mcp.tool()
def get_sample_metadata(dataset_id: str) -> Dict:
    """
    Get metadata for all samples in a dataset.
    
    Args:
        dataset_id: The ID of the dataset
    
    Returns:
        Dictionary containing sample metadata
    """
    return api_request(f"datasets/{dataset_id}/samples")

@mcp.tool()
def get_gene_expression(dataset_id: str, genes: List[str], samples: Optional[List[str]] = None) -> Dict:
    """
    Get gene expression data for specified genes and samples.
    
    Args:
        dataset_id: The ID of the dataset
        genes: List of gene identifiers
        samples: Optional list of sample IDs (returns all samples if not specified)
    
    Returns:
        Dictionary containing gene expression data
    """
    params = {"genes": ",".join(genes)}
    if samples:
        params["samples"] = ",".join(samples)
    
    return api_request(f"datasets/{dataset_id}/expression", params=params)

@mcp.tool()
def search_genes(query: str, species: Optional[str] = None, limit: int = 10) -> Dict:
    """
    Search for genes by name, symbol, or description.
    
    Args:
        query: Search query
        species: Optional species filter
        limit: Maximum number of results to return
    
    Returns:
        Dictionary containing gene search results
    """
    params = {"query": query, "limit": limit}
    if species:
        params["species"] = species
    
    return api_request(f"genes/search", params=params)

@mcp.tool()
def differential_expression(dataset_id: str, group1: List[str], group2: List[str], method: str = "limma") -> Dict:
    """
    Perform differential expression analysis between two groups of samples.
    
    Args:
        dataset_id: The ID of the dataset
        group1: List of sample IDs for group 1
        group2: List of sample IDs for group 2
        method: Statistical method to use (default: limma)
    
    Returns:
        Dictionary containing differential expression results
    """
    data = {
        "group1": group1,
        "group2": group2,
        "method": method
    }
    
    return api_request(f"datasets/{dataset_id}/differential_expression", method="POST", data=data)

@mcp.tool()
def get_pathway_analysis(dataset_id: str, gene_list: List[str], pathway_database: str = "kegg") -> Dict:
    """
    Perform pathway enrichment analysis on a list of genes.
    
    Args:
        dataset_id: The ID of the dataset
        gene_list: List of gene identifiers
        pathway_database: Pathway database to use (default: kegg)
    
    Returns:
        Dictionary containing pathway analysis results
    """
    data = {
        "genes": gene_list,
        "database": pathway_database
    }
    
    return api_request(f"datasets/{dataset_id}/pathway_analysis", method="POST", data=data)

@mcp.tool()
def get_dataset_statistics(dataset_id: str) -> Dict:
    """
    Get statistical summary of a dataset.
    
    Args:
        dataset_id: The ID of the dataset
    
    Returns:
        Dictionary containing dataset statistics
    """
    return api_request(f"datasets/{dataset_id}/statistics")

@mcp.tool()
def find_similar_samples(dataset_id: str, sample_id: str, limit: int = 10) -> Dict:
    """
    Find samples similar to a reference sample.
    
    Args:
        dataset_id: The ID of the dataset
        sample_id: The ID of the reference sample
        limit: Maximum number of similar samples to return
    
    Returns:
        Dictionary containing similar samples
    """
    params = {"sample_id": sample_id, "limit": limit}
    return api_request(f"datasets/{dataset_id}/similar_samples", params=params)

# Resources

@mcp.resource("datasets://all")
def get_all_datasets() -> Dict:
    """Get a list of all available datasets"""
    return api_request("datasets", params={"limit": 1000})

@mcp.resource("datasets://{dataset_id}")
def get_dataset_resource(dataset_id: str) -> Dict:
    """Get information about a specific dataset"""
    return api_request(f"datasets/{dataset_id}")

@mcp.resource("datasets://{dataset_id}/samples")
def get_samples_resource(dataset_id: str) -> Dict:
    """Get samples for a specific dataset"""
    return api_request(f"datasets/{dataset_id}/samples")

@mcp.resource("genes://{gene_id}")
def get_gene_resource(gene_id: str) -> Dict:
    """Get information about a specific gene"""
    return api_request(f"genes/{gene_id}")

if __name__ == "__main__":
    logger.info(f"Starting Stemformatics MCP Server with config from {CONFIG_PATH}")
    
    # Determine transport mode - default to stdio but support network as well
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    
    # For network transport, use the config settings
    if transport == "network":
        host = config["server"].get("host", "0.0.0.0")
        port = config["server"].get("port", 8080)
        logger.info(f"Starting server on {host}:{port}")
        transport_config = {"host": host, "port": port}
    else:
        # Stdio transport doesn't need additional config
        transport_config = {}
        
    logger.info(f"Using transport: {transport}")
    
    try:
        # Start the MCP server with the specified transport
        mcp.run(transport=transport, **transport_config)
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        sys.exit(1) 