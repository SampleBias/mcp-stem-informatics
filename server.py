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

@mcp.tool()
def get_dataset_pca(dataset_id: str, orient: str = "records", dims: int = 20) -> Dict:
    """
    Get PCA data for a dataset.
    
    Args:
        dataset_id: The ID of the dataset
        orient: Orientation of the data (records, list, dict, etc.)
        dims: Number of PCA dimensions to return
    
    Returns:
        Dictionary containing PCA data
    """
    params = {"orient": orient, "dims": dims}
    return api_request(f"datasets/{dataset_id}/pca", params=params)

@mcp.tool()
def get_correlated_genes(dataset_id: str, gene_id: str, cutoff: int = 30) -> Dict:
    """
    Get genes correlated with a specific gene in a dataset.
    
    Args:
        dataset_id: The ID of the dataset
        gene_id: Ensembl gene ID
        cutoff: Correlation cutoff
    
    Returns:
        Dictionary containing correlated genes
    """
    params = {"gene_id": gene_id, "cutoff": cutoff}
    return api_request(f"datasets/{dataset_id}/correlated-genes", params=params)

@mcp.tool()
def perform_ttest(dataset_id: str, gene_id: str, sample_group: str, 
                 sample_group_item1: str, sample_group_item2: str) -> Dict:
    """
    Perform t-test for a gene between two sample groups.
    
    Args:
        dataset_id: The ID of the dataset
        gene_id: Ensembl gene ID
        sample_group: Sample group key
        sample_group_item1: First sample group item
        sample_group_item2: Second sample group item
    
    Returns:
        Dictionary containing t-test results
    """
    params = {
        "gene_id": gene_id,
        "sample_group": sample_group,
        "sample_group_item1": sample_group_item1,
        "sample_group_item2": sample_group_item2
    }
    return api_request(f"datasets/{dataset_id}/ttest", params=params)

@mcp.tool()
def search_datasets(query_string: Optional[str] = None) -> Dict:
    """
    Search for datasets.
    
    Args:
        query_string: Optional search query
    
    Returns:
        Dictionary containing dataset search results
    """
    params = {}
    if query_string:
        params["query_string"] = query_string
        
    return api_request("search/datasets", params=params)

@mcp.tool()
def search_samples(query_string: Optional[str] = None, field: Optional[str] = None, 
                   limit: int = 50, orient: str = "records") -> Dict:
    """
    Search for samples.
    
    Args:
        query_string: Optional search query
        field: Optional field to search in (comma-separated)
        limit: Maximum number of results to return
        orient: Orientation of the data (records, list, dict, etc.)
    
    Returns:
        Dictionary containing sample search results
    """
    params = {"limit": limit, "orient": orient}
    
    if query_string:
        params["query_string"] = query_string
    
    if field:
        params["field"] = field
        
    return api_request("search/samples", params=params)

@mcp.tool()
def get_dataset_values(key: str, include_count: bool = False) -> Dict:
    """
    Get unique values for a specific key across all datasets.
    
    Args:
        key: Key to get values for
        include_count: Whether to include count of each value
    
    Returns:
        Dictionary containing values
    """
    params = {"include_count": str(include_count).lower()}
    return api_request(f"values/datasets/{key}", params=params)

@mcp.tool()
def get_sample_values(key: str, include_count: bool = False) -> Dict:
    """
    Get unique values for a specific key across all samples.
    
    Args:
        key: Key to get values for
        include_count: Whether to include count of each value
    
    Returns:
        Dictionary containing values
    """
    params = {"include_count": str(include_count).lower()}
    return api_request(f"values/samples/{key}", params=params)

@mcp.tool()
def download_datasets(dataset_ids: List[str]) -> Dict:
    """
    Download datasets.
    
    Args:
        dataset_ids: List of dataset IDs to download
    
    Returns:
        Dictionary containing download information
    """
    params = {"dataset_id": ",".join(map(str, dataset_ids))}
    return api_request("download", params=params)

@mcp.tool()
def get_sample_group_to_genes(sample_group: str, sample_group_item: str, cutoff: int = 10) -> Dict:
    """
    Get genes associated with a sample group.
    
    Args:
        sample_group: Sample group key
        sample_group_item: Sample group item
        cutoff: Cutoff value
    
    Returns:
        Dictionary containing gene information
    """
    params = {
        "sample_group": sample_group,
        "sample_group_item": sample_group_item,
        "cutoff": cutoff
    }
    return api_request("genes/sample-group-to-genes", params=params)

@mcp.tool()
def get_gene_to_sample_groups(gene_id: str, sample_group: str = "cell_type") -> Dict:
    """
    Get sample groups associated with a gene.
    
    Args:
        gene_id: Ensembl gene ID
        sample_group: Sample group key
    
    Returns:
        Dictionary containing sample group information
    """
    params = {"gene_id": gene_id, "sample_group": sample_group}
    return api_request("genes/gene-to-sample-groups", params=params)

@mcp.tool()
def get_atlas_types() -> Dict:
    """
    Get available atlas types.
    
    Returns:
        Dictionary containing atlas type information
    """
    return api_request("atlas-types")

@mcp.tool()
def get_atlas(atlas_type: str, item: str, version: str = "", orient: str = "records", 
              filtered: bool = False, query_string: str = "", gene_id: str = "", as_file: bool = False) -> Dict:
    """
    Get atlas data.
    
    Args:
        atlas_type: Type of atlas
        item: Atlas item
        version: Atlas version
        orient: Orientation of the data (records, list, dict, etc.)
        filtered: Whether to filter the data
        query_string: Optional search query
        gene_id: Optional Ensembl gene ID
        as_file: Whether to return the data as a file
    
    Returns:
        Dictionary containing atlas data
    """
    params = {
        "version": version,
        "orient": orient,
        "filtered": str(filtered).lower(),
        "as_file": str(as_file).lower()
    }
    
    if query_string:
        params["query_string"] = query_string
    
    if gene_id:
        params["gene_id"] = gene_id
        
    return api_request(f"atlases/{atlas_type}/{item}", params=params)

@mcp.tool()
def get_atlas_projection(atlas_type: str, data_source: str) -> Dict:
    """
    Get atlas projection data.
    
    Args:
        atlas_type: Type of atlas
        data_source: Data source
    
    Returns:
        Dictionary containing atlas projection data
    """
    return api_request(f"atlas-projection/{atlas_type}/{data_source}")

# Resources

@mcp.resource("datasets://{dataset_id}/metadata")
def get_dataset_metadata_resource(dataset_id: str) -> Dict:
    """Get metadata for a specific dataset"""
    return api_request(f"datasets/{dataset_id}/metadata")

@mcp.resource("datasets://{dataset_id}/samples")
def get_dataset_samples_resource(dataset_id: str) -> Dict:
    """Get samples for a specific dataset"""
    return api_request(f"datasets/{dataset_id}/samples")

@mcp.resource("datasets://{dataset_id}/expression")
def get_dataset_expression_resource(dataset_id: str) -> Dict:
    """Get expression data for a specific dataset"""
    return api_request(f"datasets/{dataset_id}/expression")

@mcp.resource("search://datasets")
def search_datasets_resource() -> Dict:
    """Search for datasets"""
    return api_request("search/datasets")

@mcp.resource("search://samples")
def search_samples_resource() -> Dict:
    """Search for samples"""
    return api_request("search/samples")

@mcp.resource("atlas://types")
def get_atlas_types_resource() -> Dict:
    """Get atlas types"""
    return api_request("atlas-types")

if __name__ == "__main__":
    logger.info(f"Starting Stemformatics MCP Server with config from {CONFIG_PATH}")
    
    # Determine transport mode - default to stdio but support network as well
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    
    logger.info(f"Using transport: {transport}")
    
    try:
        # Start the MCP server with the specified transport
        if transport == "network":
            host = config["server"].get("host", "0.0.0.0")
            port = config["server"].get("port", 8080)
            logger.info(f"Starting server on {host}:{port}")
            # For network transport mode, we need to use transport_config with network settings
            mcp.run(transport="sse", sse={"host": host, "port": port})
        else:
            # Stdio transport doesn't need additional config
            mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        sys.exit(1) 