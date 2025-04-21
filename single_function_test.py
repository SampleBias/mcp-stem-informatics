import json

def test_search_datasets():
    """Test the search_datasets function with a specific query"""
    print("Testing search_datasets function...")
    
    try:
        # Import the function dynamically
        from mcp_stemformatics_search_datasets import mcp_stemformatics_search_datasets
        
        # Call the function with a specific query to limit results
        result = mcp_stemformatics_search_datasets(query_string="dendritic cell")
        
        # Check the result
        if result:
            print(f"Success! Found {len(result)} datasets")
            print("First dataset:")
            print(json.dumps(result[0], indent=2))
            return True
        else:
            print("Function returned no data")
            return False
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return False

if __name__ == "__main__":
    success = test_search_datasets()
    print(f"Test {'succeeded' if success else 'failed'}") 