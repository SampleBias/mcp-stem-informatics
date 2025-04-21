# Stemformatics MCP Server

This MCP server provides access to Stemformatics data through the Model Context Protocol, allowing AI assistants like Claude to query and analyze stem cell datasets.

## What is MCP?

The Model Context Protocol (MCP) provides a standard, secure, real-time, two-way communication interface for AI systems to connect with external tools, API services, and data sources.

Unlike traditional API integration (which requires separate code, documentation, authentication methods, and maintenance), MCP provides a single, standardized way for AI models to interact with external systems. You write code once, and all AI systems can use it.

## Features

- Access dataset metadata
- Query sample information
- Retrieve gene expression data
- Perform t-tests and data analysis
- Search datasets and samples
- Access cell atlases and projections

## Setup

1. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install requirements
```bash
pip install -r requirements.txt
```

3. Configure the server
```bash
cp config.example.json config.json
# Edit config.json with your API endpoint details
```

4. Run the server
```bash
# For stdio mode (default)
python server.py

# For network mode
./run_server.sh --network  # On Windows: run_server.bat --network
```

## Connecting to Claude and Cursor

### Claude Desktop App
1. Open the Claude Desktop app
2. Go to Settings > MCP Servers
3. Click "Add MCP Server"
4. Select "Connection Type" as "Network" 
5. Enter a display name (e.g., "Stemformatics")
6. For Host, enter the IP address where your MCP server is running (e.g., "localhost" or "127.0.0.1")
7. For Port, enter the port your MCP server is listening on (default: 8080)
8. Click "Add"

### Cursor IDE
1. Open Cursor IDE
2. Go to Settings > Extensions > MCP
3. Click "Add MCP Server"
4. Enter a name for the server (e.g., "Stemformatics") 
5. For URL, enter the WebSocket URL of your MCP server (e.g., "ws://localhost:8080")
6. Click "Save"

## MCP Component Architecture

The Stemformatics MCP server follows the standard MCP architecture:

1. **Hosts**: AI applications like Claude or Cursor that need access to Stemformatics data
2. **Clients**: Maintain dedicated connections with the MCP server
3. **MCP Server**: This Stemformatics server that exposes stem cell data functionality
4. **Remote Services**: The Stemformatics API endpoints that the server communicates with

## Authentication

The server supports optional authentication with the Stemformatics API. To enable authentication:

1. Get an API key from the Stemformatics service
2. Edit the `config.json` file:
   ```json
   "auth": {
     "api_key": "YOUR_API_KEY_HERE",
     "use_auth": true
   }
   ```

## Available Tools

This MCP server provides the following tools that match the Stemformatics API:

### Dataset Operations
- `get_dataset_metadata`: Get metadata for a specific dataset
- `get_dataset_samples`: Get samples for a specific dataset
- `get_dataset_expression`: Get gene expression data for a dataset
- `get_dataset_pca`: Get PCA data for a dataset
- `get_correlated_genes`: Get genes correlated with a specific gene
- `perform_ttest`: Perform t-test for a gene between two sample groups

### Search and Values
- `search_datasets`: Search for datasets
- `search_samples`: Search for samples
- `get_dataset_values`: Get unique values for a dataset field
- `get_sample_values`: Get unique values for a sample field

### Atlas and Gene Operations
- `get_atlas_types`: Get available atlas types
- `get_atlas`: Get atlas data
- `get_atlas_projection`: Get atlas projection data
- `get_sample_group_to_genes`: Get genes associated with a sample group
- `get_gene_to_sample_groups`: Get sample groups associated with a gene

## Example Usage

Here's an example of how to use the Stemformatics API directly:

```python
# Python example
import pandas, requests
r = requests.get('https://api.stemformatics.org/datasets/2000/samples')
df = pandas.DataFrame(r.json())
print(df.head())

# Search for samples
r = requests.get('https://api.stemformatics.org/search/samples?query_string=%s&field=tissue_of_origin,dataset_id' % 'dendritic cell')
print(r.json()[:2])

# Get expression matrix as file and read into pandas
import io
r = requests.get('https://api.stemformatics.org/datasets/6756/expression?as_file=true')
df = pandas.read_csv(io.StringIO(r.text), sep='\t', index_col=0)
print(df.head())
```

With this MCP server, the same functionality is available to AI assistants through the MCP protocol.
