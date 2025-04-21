import json
import time

def search_datasets_small_query():
    """
    Search for a small number of datasets using the MCP function
    """
    print("Searching for datasets with a limited query...")
    
    try:
        # This function call will be handled by Cursor's MCP interface
        from mcp_stemformatics_search_datasets import mcp_stemformatics_search_datasets
        
        # Use a specific query to limit results
        datasets = mcp_stemformatics_search_datasets(query_string="dendritic cell")
        
        if not datasets:
            print("No datasets found")
            return []
            
        print(f"Retrieved {len(datasets)} datasets")
        return datasets
        
    except Exception as e:
        print(f"Error searching for datasets: {e}")
        return []

def get_samples_for_dataset(dataset_id):
    """
    Get samples for a specific dataset using MCP
    
    Args:
        dataset_id: ID of the dataset to retrieve samples for
    """
    print(f"Getting samples for dataset {dataset_id}")
    
    try:
        from mcp_stemformatics_get_dataset_samples import mcp_stemformatics_get_dataset_samples
        
        # Get the samples
        samples = mcp_stemformatics_get_dataset_samples(
            dataset_id=dataset_id, 
            orient="records"
        )
        
        if not samples:
            print(f"No samples found for dataset {dataset_id}")
            return []
            
        print(f"Retrieved samples for dataset {dataset_id}")
        return samples
        
    except Exception as e:
        print(f"Error getting samples for dataset {dataset_id}: {e}")
        return []

def get_dataset_details(dataset_id):
    """
    Get detailed metadata for a specific dataset using MCP
    
    Args:
        dataset_id: ID of the dataset to retrieve metadata for
    """
    print(f"Getting metadata for dataset {dataset_id}")
    
    try:
        from mcp_stemformatics_get_dataset_metadata import mcp_stemformatics_get_dataset_metadata
        
        # Get the metadata
        metadata = mcp_stemformatics_get_dataset_metadata(dataset_id=dataset_id)
        
        if not metadata:
            print(f"No metadata found for dataset {dataset_id}")
            return {}
            
        print(f"Retrieved metadata for dataset {dataset_id}")
        return metadata
        
    except Exception as e:
        print(f"Error getting metadata for dataset {dataset_id}: {e}")
        return {}

def search_all_samples_limited(query_string="dendritic cell", limit=10):
    """
    Search for a limited number of samples using MCP
    
    Args:
        query_string: Search term
        limit: Maximum number of results to return
    """
    print(f"Searching for samples with query: {query_string}")
    
    try:
        from mcp_stemformatics_search_samples import mcp_stemformatics_search_samples
        
        # Search for samples with a limited result set
        samples = mcp_stemformatics_search_samples(
            query_string=query_string,
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
    # Example 1: Search for a small number of datasets
    datasets = search_datasets_small_query()
    
    if datasets:
        # Save the datasets to a file
        save_data_to_file(datasets, "mcp_limited_datasets.json")
        
        # Example 2: Get metadata for one dataset
        if len(datasets) > 0:
            dataset = datasets[0]
            dataset_id = dataset.get("dataset_id") 
            
            if dataset_id:
                # Get detailed metadata for the dataset
                metadata = get_dataset_details(dataset_id)
                if metadata:
                    save_data_to_file(metadata, f"metadata_dataset_{dataset_id}.json")
    
    # Example 3: Search for a limited number of samples
    samples = search_all_samples_limited(limit=10)
    if samples:
        save_data_to_file(samples, "limited_dendritic_cell_samples.json") 