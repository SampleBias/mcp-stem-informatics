import json
import time
from mcp_stemformatics import (
    get_dataset_expression,
    search_datasets,
    get_dataset_metadata
)

def get_expression_data_in_chunks(dataset_id, genes=None, chunk_size=5, delay_seconds=2):
    """
    Retrieve gene expression data for a dataset, one gene at a time
    to avoid overwhelming the server
    
    Args:
        dataset_id: ID of the dataset to retrieve expression data for
        genes: List of gene IDs to retrieve, if None will retrieve all genes one by one
        chunk_size: Number of genes to retrieve in one batch (if supported)
        delay_seconds: Delay between requests to reduce server load
    """
    if genes is None:
        # First get dataset metadata to see what genes are available
        try:
            print(f"Getting metadata for dataset {dataset_id} to identify genes...")
            metadata = get_dataset_metadata(dataset_id=dataset_id)
            
            # This is hypothetical; actual implementation depends on how genes are represented in metadata
            if metadata and 'genes' in metadata:
                genes = metadata['genes']
                print(f"Found {len(genes)} genes in metadata")
            else:
                print("Could not find gene information in metadata. Will retrieve all expression data at once.")
                return get_all_expression_data(dataset_id)
                
        except Exception as e:
            print(f"Error getting metadata: {e}")
            return None
    
    all_expression_data = {}
    
    # Retrieve expression data for each gene
    for i, gene_id in enumerate(genes):
        print(f"Retrieving expression data for gene {gene_id} ({i+1}/{len(genes)})")
        
        try:
            gene_data = get_dataset_expression(
                dataset_id=dataset_id,
                gene_id=gene_id,
                orient="records"
            )
            
            if gene_data:
                all_expression_data[gene_id] = gene_data
                print(f"Successfully retrieved data for gene {gene_id}")
            else:
                print(f"No expression data found for gene {gene_id}")
                
            # Delay to avoid overwhelming the server
            if (i+1) % chunk_size == 0:
                print(f"Processed {i+1} genes, pausing for {delay_seconds} seconds...")
                time.sleep(delay_seconds)
                
        except Exception as e:
            print(f"Error retrieving expression data for gene {gene_id}: {e}")
            # Continue with the next gene
            continue
    
    print(f"Retrieved expression data for {len(all_expression_data)} genes")
    return all_expression_data

def get_all_expression_data(dataset_id):
    """
    Retrieve all expression data for a dataset at once
    
    Args:
        dataset_id: ID of the dataset to retrieve expression data for
    """
    print(f"Retrieving all expression data for dataset {dataset_id}")
    
    try:
        expression_data = get_dataset_expression(
            dataset_id=dataset_id,
            gene_id=None,  # Retrieve all genes
            orient="records"
        )
        
        if expression_data:
            print(f"Successfully retrieved all expression data")
            return expression_data
        else:
            print(f"No expression data found")
            return None
            
    except Exception as e:
        print(f"Error retrieving expression data: {e}")
        return None

def save_data_to_file(data, filename):
    """Save data to a JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {filename}")

def find_datasets_with_expression_data(query_string=None):
    """
    Find datasets that likely have expression data
    
    Args:
        query_string: Optional search term to find specific datasets
    """
    print("Searching for datasets that likely have expression data...")
    
    try:
        datasets = search_datasets(query_string=query_string)
        
        if not datasets:
            print("No datasets found")
            return []
            
        print(f"Found {len(datasets)} datasets, checking for expression data...")
        
        # Filter datasets that mention expression in their description or title
        expression_datasets = []
        for dataset in datasets:
            title = dataset.get('title', '').lower()
            description = dataset.get('description', '').lower()
            
            if ('expression' in title or 'expression' in description) and dataset.get('dataset_id'):
                expression_datasets.append(dataset)
                
        print(f"Found {len(expression_datasets)} datasets that likely have expression data")
        return expression_datasets
        
    except Exception as e:
        print(f"Error searching for datasets: {e}")
        return []

if __name__ == "__main__":
    # Example 1: Find datasets with expression data
    expression_datasets = find_datasets_with_expression_data()
    
    if expression_datasets:
        # Save list of expression datasets
        save_data_to_file(expression_datasets, "expression_datasets.json")
        
        # Example 2: Get expression data for a single dataset
        if len(expression_datasets) > 0:
            dataset_id = expression_datasets[0].get('dataset_id')
            
            if dataset_id:
                # Get all expression data at once for a small dataset
                all_expression = get_all_expression_data(dataset_id)
                
                if all_expression:
                    save_data_to_file(all_expression, f"all_expression_dataset_{dataset_id}.json")
                
                # Example 3: Get expression data for specific genes
                # Define some example genes (these are example Ensembl IDs)
                example_genes = ["ENSG00000118513", "ENSG00000141510", "ENSG00000157764"]
                
                gene_expression = get_expression_data_in_chunks(
                    dataset_id=dataset_id,
                    genes=example_genes,
                    chunk_size=2,
                    delay_seconds=3
                )
                
                if gene_expression:
                    save_data_to_file(
                        gene_expression, 
                        f"gene_expression_dataset_{dataset_id}.json"
                    ) 