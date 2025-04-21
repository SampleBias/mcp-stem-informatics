#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
# Set environment variables
export PYTHONUNBUFFERED=1
export LOGGING_LEVEL=ERROR
# Run the modified server that uses stderr for logging
exec python -u server_mcp.py 2>/tmp/stemformatics-mcp.error.log 