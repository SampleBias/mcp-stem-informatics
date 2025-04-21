import requests
import json
import time

def retrieve_datasets_in_chunks(chunk_size=10, delay_seconds=1):
    """
    Retrieve dataset information in manageable chunks
    
    Args:
        chunk_size: Number of datasets to retrieve per request
        delay_seconds: Delay between requests to reduce server load
    """
    base_url = "https://api.stemformatics.org/search/datasets"
    
    # Initial request to get all datasets (but with pagination)
    params = {
        "pagination_limit": chunk_size,
        "pagination_start": 0
    }
    
    all_datasets = []
    
    while True:
        print(f"Retrieving datasets {params['pagination_start']} to {params['pagination_start'] + params['pagination_limit']}...")
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Get the data
            datasets = response.json()
            
            # Check if we've reached the end
            if not datasets:
                print("Reached the end of the dataset list.")
                break
                
            # Add to our collection
            all_datasets.extend(datasets)
            print(f"Retrieved {len(datasets)} datasets")
            
            # Move to the next chunk
            params["pagination_start"] += params["pagination_limit"]
            
            # Sleep to avoid overwhelming the server
            time.sleep(delay_seconds)
            
        except Exception as e:
            print(f"Error retrieving datasets: {e}")
            break
    
    print(f"Total datasets retrieved: {len(all_datasets)}")
    return all_datasets

def retrieve_samples_for_dataset(dataset_id, chunk_size=20, delay_seconds=1):
    """
    Retrieve samples for a specific dataset in chunks
    
    Args:
        dataset_id: ID of the dataset to retrieve samples for
        chunk_size: Number of samples to retrieve per request
        delay_seconds: Delay between requests to reduce server load
    """
    base_url = f"https://api.stemformatics.org/datasets/{dataset_id}/samples"
    
    params = {
        "limit": chunk_size,
        "orient": "records",
        "as_file": False
    }
    
    all_samples = []
    
    while True:
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Get the data
            samples = response.json()
            
            # Check if we've reached the end
            if not samples:
                print(f"Retrieved all samples for dataset {dataset_id}")
                break
                
            # Add to our collection
            all_samples.extend(samples)
            print(f"Retrieved {len(samples)} samples for dataset {dataset_id}")
            
            # If we got fewer samples than the chunk size, we're done
            if len(samples) < chunk_size:
                break
                
            # Move to the next chunk (implementation depends on API pagination)
            # This may need adjustment based on the actual API behavior
            params["offset"] = len(all_samples)
            
            # Sleep to avoid overwhelming the server
            time.sleep(delay_seconds)
            
        except Exception as e:
            print(f"Error retrieving samples for dataset {dataset_id}: {e}")
            break
    
    print(f"Total samples retrieved for dataset {dataset_id}: {len(all_samples)}")
    return all_samples

def save_data_to_file(data, filename):
    """Save data to a JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    # Example usage: Retrieve datasets in chunks
    datasets = retrieve_datasets_in_chunks(chunk_size=5, delay_seconds=2)
    
    if datasets:
        # Save the datasets to a file
        save_data_to_file(datasets, "stemformatics_datasets.json")
        
        # Example: Retrieve samples for the first dataset
        if len(datasets) > 0:
            first_dataset_id = datasets[0]["dataset_id"]
            samples = retrieve_samples_for_dataset(first_dataset_id, chunk_size=10, delay_seconds=2)
            
            if samples:
                save_data_to_file(samples, f"samples_dataset_{first_dataset_id}.json") 