#!/usr/bin/env python3
"""
MCP Server Wrapper

This script acts as a middleware between Claude Desktop and the MCP server
to fix JSON formatting issues and ensure proper communication.
"""

import sys
import os
import json
import logging
import subprocess
import re
from typing import Optional, Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("/tmp/mcp_wrapper.log")]
)
logger = logging.getLogger("mcp-wrapper")

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_SCRIPT = os.path.join(SCRIPT_DIR, "server_mcp.py")

# Get Python executable from environment or use current one
PYTHON_EXE = os.environ.get("PYTHON_BIN", sys.executable)
logger.info(f"Using Python executable: {PYTHON_EXE}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Script directory: {SCRIPT_DIR}")
logger.info(f"Server script: {SERVER_SCRIPT}")

def fix_json(data: str) -> str:
    """Fix common JSON formatting issues"""
    # Log the raw input for debugging
    logger.debug(f"Raw input: {data[:200]}")
    
    try:
        # Check if it's already valid JSON
        json.loads(data)
        logger.debug("JSON is already valid")
        return data
    except json.JSONDecodeError as e:
        logger.debug(f"JSON decode error: {e}, attempting to fix")
        
        # Attempt multiple fix strategies
        
        # 1. Find complete JSON object
        try:
            opening_brackets = 0
            closing_brackets = 0
            in_quotes = False
            escape_next = False
            start_idx = data.find('{')
            
            if start_idx == -1:
                logger.debug("No JSON object found")
                return data
                
            for i in range(start_idx, len(data)):
                char = data[i]
                
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                    continue
                    
                if char == '"' and not escape_next:
                    in_quotes = not in_quotes
                    continue
                    
                if not in_quotes:
                    if char == '{':
                        opening_brackets += 1
                    elif char == '}':
                        closing_brackets += 1
                        
                    if opening_brackets > 0 and opening_brackets == closing_brackets:
                        # Found complete JSON object
                        json_part = data[start_idx:i+1]
                        try:
                            # Verify it's valid
                            json.loads(json_part)
                            logger.debug(f"Found valid JSON object: {json_part[:50]}...")
                            return json_part
                        except json.JSONDecodeError:
                            # Not valid, continue searching
                            pass
        except Exception as e:
            logger.debug(f"Error in bracket matching: {e}")
        
        # 2. Try regular expression approaches
        try:
            # Try to match a complete JSON object
            pattern = r'(\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\})'
            matches = re.findall(pattern, data)
            
            for match in matches:
                try:
                    # Verify it's valid JSON
                    json.loads(match)
                    logger.debug(f"Found valid JSON via regex: {match[:50]}...")
                    return match
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            logger.debug(f"Error in regex approach: {e}")
            
        # 3. Last resort: Look for content-type header and attempt to find JSON
        try:
            if "content-type" in data.lower() and "application/json" in data.lower():
                # Try to extract JSON after the headers
                parts = data.split("\r\n\r\n", 1)
                if len(parts) > 1:
                    try:
                        json.loads(parts[1])
                        logger.debug("Found JSON after headers")
                        return parts[1]
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            logger.debug(f"Error in header extraction: {e}")
    
    # All fixes failed, return the original
    logger.debug(f"Could not fix JSON, returning original: {data[:100]}...")
    return data

def main():
    logger.info("Starting MCP wrapper")
    
    # Launch the server_mcp.py script with the specified Python executable
    process = subprocess.Popen(
        [PYTHON_EXE, SERVER_SCRIPT],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # Line buffered
        cwd=SCRIPT_DIR  # Set working directory to script directory
    )
    
    def process_output():
        """Process and fix JSON from server output"""
        logger.info("Starting output processor thread")
        while True:
            line = process.stdout.readline()
            if not line:
                logger.info("Output stream closed")
                break
                
            try:
                logger.debug(f"Raw output: {line[:100]}")
                fixed_line = fix_json(line)
                sys.stdout.write(fixed_line)
                sys.stdout.flush()
            except Exception as e:
                logger.error(f"Error processing output: {e}")
                # Still try to write something
                sys.stdout.write(line)
                sys.stdout.flush()
    
    def process_input():
        """Forward input from stdin to the server process"""
        logger.info("Starting input processor thread")
        try:
            for line in sys.stdin:
                try:
                    logger.debug(f"Input: {line[:100]}")
                    process.stdin.write(line)
                    process.stdin.flush()
                except Exception as e:
                    logger.error(f"Error forwarding input: {e}")
        except Exception as e:
            logger.error(f"Fatal error in input processing: {e}")
    
    def process_errors():
        """Log errors from the server"""
        logger.info("Starting error processor thread")
        for line in process.stderr:
            logger.error(f"Server error: {line.strip()}")
    
    # Handle the server's output, input, and errors
    import threading
    output_thread = threading.Thread(target=process_output, daemon=True)
    error_thread = threading.Thread(target=process_errors, daemon=True)
    
    output_thread.start()
    error_thread.start()
    
    try:
        process_input()
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt, shutting down")
    finally:
        logger.info("Terminating MCP server")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("Process did not terminate in time, killing")
            process.kill()
        
        # Wait for threads to finish
        output_thread.join(timeout=2)
        error_thread.join(timeout=2)

if __name__ == "__main__":
    main() 