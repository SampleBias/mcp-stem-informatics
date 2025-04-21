#!/bin/bash

# Diagnostic script for Stemformatics MCP server
# This script helps verify that everything is set up correctly

echo "=== Hammer Check - Stemformatics MCP Server Diagnostics ==="
echo "Running diagnostics at $(date)"
echo

# Check Python versions
echo "=== Python versions ==="
echo "System Python:"
which python3 || which python || echo "Python not found in PATH"
python3 -V 2>/dev/null || python -V 2>/dev/null || echo "Cannot determine Python version"
echo

# Check virtual environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"
echo "=== Virtual Environment ==="
echo "Virtual environment path: ${VENV_DIR}"
if [ -d "${VENV_DIR}" ]; then
  echo "Virtual environment exists: YES"
  if [ -f "${VENV_DIR}/bin/python" ]; then
    echo "Virtual environment Python: YES"
    echo "Python version:"
    "${VENV_DIR}/bin/python" -V
    echo "Python packages:"
    "${VENV_DIR}/bin/pip" list | grep -E 'mcp|fastapi|pandas|numpy|requests'
  else
    echo "Virtual environment Python: NO"
  fi
else
  echo "Virtual environment exists: NO"
fi
echo

# Check script permissions
echo "=== Script Permissions ==="
ls -la "${SCRIPT_DIR}/run_mcp_wrapper.sh" "${SCRIPT_DIR}/mcp_wrapper.py" "${SCRIPT_DIR}/server_mcp.py"
echo

# Check if important files exist
echo "=== Important Files ==="
for file in server_mcp.py mcp_wrapper.py run_mcp_wrapper.sh config.json; do
  if [ -f "${SCRIPT_DIR}/${file}" ]; then
    echo "${file}: EXISTS"
  else
    echo "${file}: MISSING"
  fi
done
echo

# Check if Python can import required modules
echo "=== Python Module Check ==="
PYTHON_PATH="${VENV_DIR}/bin/python"
if [ ! -f "${PYTHON_PATH}" ]; then
  PYTHON_PATH=$(which python3 || which python)
fi

echo "Using Python: ${PYTHON_PATH}"
for module in sys os json logging subprocess re typing pandas numpy requests mcp.server.fastmcp dotenv; do
  echo -n "Import ${module}: "
  "${PYTHON_PATH}" -c "import ${module}" 2>/dev/null && echo "SUCCESS" || echo "FAILED"
done
echo

# Try running the scripts with absolute paths
echo "=== Testing Script Execution ==="
echo "Testing wrapper script (will terminate after 2 seconds)..."
"${SCRIPT_DIR}/run_mcp_wrapper.sh" &
WRAPPER_PID=$!
sleep 2
kill $WRAPPER_PID 2>/dev/null
echo "Check log files for details:"
echo "- /tmp/stemformatics-mcp-startup.log"
echo "- /tmp/mcp_wrapper.log"
echo "- /tmp/stemformatics-mcp-wrapper.error.log"
echo

# Display recent error logs
echo "=== Recent Error Logs ==="
if [ -f "/tmp/mcp_wrapper.log" ]; then
  echo "Last 10 lines of wrapper log:"
  tail -n 10 "/tmp/mcp_wrapper.log"
  echo
fi

if [ -f "/tmp/stemformatics-mcp-wrapper.error.log" ]; then
  echo "Last 10 lines of wrapper error log:"
  tail -n 10 "/tmp/stemformatics-mcp-wrapper.error.log"
  echo
fi

echo "=== Diagnostics Complete ==="
echo "If you're still encountering issues, please check:"
echo "1. Python and virtual environment setup"
echo "2. MCP package installation"
echo "3. File permissions"
echo "4. Configuration files"
echo
echo "You can also try running the server directly:"
echo "cd ${SCRIPT_DIR} && source venv/bin/activate && python server_mcp.py" 