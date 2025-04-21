#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
# Set environment variables to redirect logging to stderr
export PYTHONUNBUFFERED=1
export LOGGING_LEVEL=ERROR
export MCP_LOG_TO_STDERR=1
# This is critical: redirect all logging to stderr
export PYTHONIOENCODING=utf-8
exec python -u -c "
import os
import sys
import logging

# Redirect all logging to stderr before importing anything else
root_logger = logging.getLogger()
root_logger.setLevel(logging.ERROR)
handler = logging.StreamHandler(sys.stderr)
root_logger.addHandler(handler)

# Now import and run the server
import server
" 2>/tmp/stemformatics-mcp.error.log
