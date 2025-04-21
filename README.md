# Stemformatics MCP Server

This MCP server provides access to Stemformatics data through the Model Context Protocol, allowing AI assistants to query and analyze stem cell datasets.

## Features

- Access dataset metadata
- Query sample information
- Retrieve gene expression data
- Perform basic data analysis

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
python server.py
```

## Usage

The MCP server can be used with any MCP-compatible client, such as Anthropic's Claude, Cursor IDE, or other AI assistants that support the Model Context Protocol.
