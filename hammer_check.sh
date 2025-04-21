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

# Use virtual environment Python if available
PYTHON_PATH="${VENV_DIR}/bin/python"
if [ ! -f "${PYTHON_PATH}" ]; then
  PYTHON_PATH=$(which python3 || which python)
fi

# Check MCP package installation
echo "=== MCP Package Inspection ==="
echo "MCP package location:"
"${PYTHON_PATH}" -c "import mcp; print(mcp.__file__)" 2>/dev/null || echo "MCP package not found"
echo "MCP package version:"
"${PYTHON_PATH}" -c "import mcp; print(getattr(mcp, '__version__', 'Version not found'))" 2>/dev/null || echo "Could not determine MCP version"
echo

# Check if Python can import required modules
echo "=== Python Module Check ==="
echo "Using Python: ${PYTHON_PATH}"
for module in sys os json logging subprocess re typing pandas numpy requests mcp.server.fastmcp dotenv; do
  echo -n "Import ${module}: "
  "${PYTHON_PATH}" -c "import ${module}" 2>/dev/null && echo "SUCCESS" || echo "FAILED"
done
echo

# Check transport modes
echo "=== MCP Transport Configuration ==="
echo "Direct server config:"
grep -A5 "transport" "${SCRIPT_DIR}/server_mcp.py" || echo "Could not find transport config in server_mcp.py"
echo
echo "Wrapper transport setting:"
grep -n "MCP_TRANSPORT" "${SCRIPT_DIR}/run_mcp_wrapper.sh" || echo "No MCP_TRANSPORT in run_mcp_wrapper.sh"
echo

# Try running the MCP server directly with stdio transport to test
echo "=== Direct Server Test ==="
echo "Testing MCP server directly with stdio transport (will terminate after 3 seconds)..."
(cd "${SCRIPT_DIR}" && source "${VENV_DIR}/bin/activate" && MCP_TRANSPORT=stdio python -u server_mcp.py) & 
SERVER_PID=$!
sleep 3
kill $SERVER_PID 2>/dev/null
echo

# Try running the scripts with absolute paths
echo "=== Wrapper Script Test ==="
echo "Testing wrapper script (will terminate after 3 seconds)..."
"${SCRIPT_DIR}/run_mcp_wrapper.sh" &
WRAPPER_PID=$!
sleep 3
kill $WRAPPER_PID 2>/dev/null
echo "Check log files for details:"
echo "- /tmp/stemformatics-mcp-startup.log"
echo "- /tmp/mcp_wrapper.log"
echo "- /tmp/stemformatics-mcp-wrapper.error.log"
echo

# Display recent error logs
echo "=== Recent Error Logs ==="
if [ -f "/tmp/mcp_wrapper.log" ]; then
  echo "Last 15 lines of wrapper log:"
  tail -n 15 "/tmp/mcp_wrapper.log"
  echo
fi

if [ -f "/tmp/stemformatics-mcp-wrapper.error.log" ]; then
  echo "Last 15 lines of wrapper error log:"
  tail -n 15 "/tmp/stemformatics-mcp-wrapper.error.log"
  echo
fi

if [ -f "/tmp/stemformatics-mcp-startup.log" ]; then
  echo "Startup log:"
  cat "/tmp/stemformatics-mcp-startup.log"
  echo
fi

echo "=== MCP Environment Variables ==="
env | grep -i MCP
echo

echo "=== Diagnostics Complete ==="
echo "If you're still encountering issues, please check:"
echo "1. Make sure MCP package is installed properly: pip install mcp-python-client"
echo "2. Ensure the transport mode is set to 'stdio' in both wrapper and server"
echo "3. Check all permissions and files exist"
echo "4. Verify that the Claude Desktop config points to the correct script"
echo "5. Try starting the server standalone to see if it works:"
echo "   cd ${SCRIPT_DIR} && source venv/bin/activate && MCP_TRANSPORT=stdio python -u server_mcp.py"
echo
echo "You may also need to check if the MCP server implementation is compatible with"
echo "the Claude Desktop's MCP client implementation version." 