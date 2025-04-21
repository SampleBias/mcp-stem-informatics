#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
exec python -u server.py 2>/tmp/stemformatics-mcp.error.log
