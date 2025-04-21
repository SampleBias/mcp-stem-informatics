#!/bin/bash
# Script to run the Stemformatics MCP Server

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

# Check for transport mode
if [ "$1" == "--network" ]; then
    # Run in network mode
    echo "Starting Stemformatics MCP Server in network mode..."
    export MCP_TRANSPORT=network
    python server.py
else
    # Default to stdio mode
    echo "Starting Stemformatics MCP Server in stdio mode..."
    export MCP_TRANSPORT=stdio
    python server.py
fi

# Deactivate virtual environment on exit
deactivate 