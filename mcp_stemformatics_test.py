import json
import time
from mcp_stemformatics import (
    search_datasets,
    get_dataset_metadata,
    get_dataset_samples,
    search_samples
)

def search_datasets_in_chunks(query_string=None, chunk_size=10, delay_seconds=1):
    """
    Search for datasets using MCP and retrieve them in manageable chunks
    
    Args:
        query_string: Optional search term
        chunk_size: Number of datasets to retrieve per call
        delay_seconds: Delay between calls to reduce server load
    """
    print(f"Searching for datasets with query: {query_string or 'All datasets'}")
    
    try:
        # Start with the initial search
        datasets = search_datasets(query_string=query_string)
        
        if not datasets or not isinstance(datasets, list):
            print("No datasets found or invalid response format")
            return []
            
        print(f"Retrieved {len(datasets)} datasets")
        return datasets
        
    except Exception as e:
        print(f"Error searching for datasets: {e}")
        return []

def get_samples_for_dataset(dataset_id, delay_seconds=1):
    """
    Get samples for a specific dataset using MCP
    
    Args:
        dataset_id: ID of the dataset to retrieve samples for
        delay_seconds: Delay between calls to reduce server load
    """
    print(f"Getting samples for dataset {dataset_id}")
    
    try:
        # Get the samples
        samples = get_dataset_samples(dataset_id=dataset_id, orient="records")
        
        if not samples:
            print(f"No samples found for dataset {dataset_id}")
            return []
            
        print(f"Retrieved {len(samples)} samples for dataset {dataset_id}")
        return samples
        
    except Exception as e:
        print(f"Error getting samples for dataset {dataset_id}: {e}")
        return []

def get_dataset_details(dataset_id, delay_seconds=1):
    """
    Get detailed metadata for a specific dataset using MCP
    
    Args:
        dataset_id: ID of the dataset to retrieve metadata for
        delay_seconds: Delay between calls to reduce server load
    """
    print(f"Getting metadata for dataset {dataset_id}")
    
    try:
        # Get the metadata
        metadata = get_dataset_metadata(dataset_id=dataset_id)
        
        if not metadata:
            print(f"No metadata found for dataset {dataset_id}")
            return {}
            
        print(f"Retrieved metadata for dataset {dataset_id}")
        return metadata
        
    except Exception as e:
        print(f"Error getting metadata for dataset {dataset_id}: {e}")
        return {}

def search_all_samples(query_string=None, field=None, limit=50):
    """
    Search for samples using MCP
    
    Args:
        query_string: Optional search term
        field: Optional field to search in
        limit: Maximum number of results to return
    """
    print(f"Searching for samples with query: {query_string or 'All samples'}")
    
    try:
        # Search for samples
        samples = search_samples(
            query_string=query_string,
            field=field,
            limit=limit,
            orient="records"
        )
        
        if not samples:
            print("No samples found")
            return []
            
        print(f"Retrieved {len(samples)} samples")
        return samples
        
    except Exception as e:
        print(f"Error searching for samples: {e}")
        return []

def save_data_to_file(data, filename):
    """Save data to a JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    # Example 1: Search for all datasets
    datasets = search_datasets_in_chunks()
    
    if datasets:
        # Save the datasets to a file
        save_data_to_file(datasets, "mcp_stemformatics_datasets.json")
        
        # Example 2: Get samples for the first dataset
        if len(datasets) > 0:
            first_dataset = datasets[0]
            first_dataset_id = first_dataset.get("dataset_id")
            
            if first_dataset_id:
                # Get detailed metadata for the dataset
                metadata = get_dataset_details(first_dataset_id)
                if metadata:
                    save_data_to_file(metadata, f"metadata_dataset_{first_dataset_id}.json")
                
                # Get samples for the dataset
                samples = get_samples_for_dataset(first_dataset_id)
                if samples:
                    save_data_to_file(samples, f"samples_dataset_{first_dataset_id}.json")
    
    # Example 3: Search for samples with a specific query
    samples = search_all_samples(query_string="dendritic cell", limit=20)
    if samples:
        save_data_to_file(samples, "dendritic_cell_samples.json") 