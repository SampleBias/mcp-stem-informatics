#!/bin/bash
# Simple script to run the Stemformatics MCP server

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if virtual environment exists, create if it doesn't
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if config file exists
if [ ! -f "config.json" ] && [ -f "config.example.json" ]; then
    echo "Config file not found. Creating from example..."
    cp config.example.json config.json
    echo "Please edit config.json with your API settings."
fi

# Run the server with MCP CLI
echo "Starting Stemformatics MCP Server..."
python -m mcp dev server.py

# Deactivate virtual environment on exit
deactivate 