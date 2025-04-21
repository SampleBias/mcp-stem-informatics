#!/bin/bash

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"

# Check if virtualenv exists
if [ ! -d "${VENV_DIR}" ]; then
  echo "Virtual environment not found at ${VENV_DIR}" >&2
  exit 1
fi

# Source virtual environment with full path
source "${VENV_DIR}/bin/activate"

# Set environment variables
export PYTHONUNBUFFERED=1
export LOGGING_LEVEL=ERROR
export PYTHONIOENCODING=utf-8

# Use full path to Python from virtualenv
PYTHON_BIN="${VENV_DIR}/bin/python"

# Verify Python executable exists
if [ ! -f "${PYTHON_BIN}" ]; then
  echo "Python executable not found at ${PYTHON_BIN}" >&2
  # Fallback to system Python
  PYTHON_BIN=$(which python3 || which python)
  echo "Falling back to system Python: ${PYTHON_BIN}" >&2
fi

# Export Python path for the wrapper script
export PYTHON_BIN

# Run the wrapper script with diagnostics
echo "Starting MCP Wrapper with Python: ${PYTHON_BIN}" >/tmp/stemformatics-mcp-startup.log
"${PYTHON_BIN}" -V >>/tmp/stemformatics-mcp-startup.log 2>&1
echo "Working directory: $(pwd)" >>/tmp/stemformatics-mcp-startup.log
echo "PATH: $PATH" >>/tmp/stemformatics-mcp-startup.log
ls -la "${SCRIPT_DIR}"/*.py >>/tmp/stemformatics-mcp-startup.log 2>&1

# Run the wrapper script
exec "${PYTHON_BIN}" -u "${SCRIPT_DIR}/mcp_wrapper.py" 2>/tmp/stemformatics-mcp-wrapper.error.log 